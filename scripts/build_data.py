from __future__ import annotations

import json
import math
import struct
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
OUT = ROOT / "data" / "generated" / "quadras.json"
SEARCH_RADIUS_M = 25.0
GRID_SIZE_M = 500.0


def read_dbf(path: Path) -> list[dict[str, str]]:
    data = path.read_bytes()
    count = struct.unpack("<I", data[4:8])[0]
    header_len = struct.unpack("<H", data[8:10])[0]
    record_len = struct.unpack("<H", data[10:12])[0]
    encoding = "utf-8"
    cpg = path.with_suffix(".cpg")
    if cpg.exists():
        value = cpg.read_text(encoding="ascii", errors="ignore").strip().lower()
        if value in {"1252", "windows-1252", "cp1252"}:
            encoding = "cp1252"
    fields = []
    offset = 32
    while data[offset] != 0x0D:
        descriptor = data[offset:offset + 32]
        name = descriptor[:11].split(b"\0", 1)[0].decode("ascii", "replace")
        fields.append((name, descriptor[16]))
        offset += 32
    rows = []
    for index in range(count):
        offset = header_len + index * record_len
        deleted = data[offset:offset + 1] == b"*"
        offset += 1
        row = {}
        for name, size in fields:
            raw = data[offset:offset + size]
            offset += size
            row[name] = raw.decode(encoding, "replace").strip()
        if not deleted:
            rows.append(row)
        else:
            rows.append({})
    return rows


def read_shp(path: Path) -> list[dict]:
    data = path.read_bytes()
    shapes = []
    offset = 100
    while offset + 8 <= len(data):
        content_length = struct.unpack(">i", data[offset + 4:offset + 8])[0] * 2
        content = data[offset + 8:offset + 8 + content_length]
        offset += 8 + content_length
        if len(content) < 4:
            shapes.append({"bbox": None, "parts": []})
            continue
        shape_type = struct.unpack("<i", content[:4])[0]
        if shape_type == 0 or shape_type not in {3, 5, 13, 15} or len(content) < 44:
            shapes.append({"bbox": None, "parts": []})
            continue
        bbox = struct.unpack("<4d", content[4:36])
        part_count, point_count = struct.unpack("<2i", content[36:44])
        part_offsets = struct.unpack("<" + "i" * part_count, content[44:44 + 4 * part_count])
        point_offset = 44 + 4 * part_count
        points = [
            struct.unpack("<2d", content[point_offset + 16 * i:point_offset + 16 * i + 16])
            for i in range(point_count)
        ]
        parts = []
        for i, start in enumerate(part_offsets):
            end = part_offsets[i + 1] if i + 1 < part_count else point_count
            parts.append(points[start:end])
        shapes.append({"bbox": bbox, "parts": parts})
    return shapes


def ring_area_and_centroid(ring):
    twice_area = 0.0
    cx = cy = 0.0
    for i, point in enumerate(ring):
        nxt = ring[(i + 1) % len(ring)]
        cross = point[0] * nxt[1] - nxt[0] * point[1]
        twice_area += cross
        cx += (point[0] + nxt[0]) * cross
        cy += (point[1] + nxt[1]) * cross
    if abs(twice_area) < 1e-9:
        return 0.0, (sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring))
    return twice_area / 2.0, (cx / (3.0 * twice_area), cy / (3.0 * twice_area))


def polygon_center(parts):
    rings = [ring for ring in parts if len(ring) >= 3]
    if not rings:
        return None
    ring = max(rings, key=lambda item: abs(ring_area_and_centroid(item)[0]))
    return ring_area_and_centroid(ring)[1]


def point_in_ring(point, ring):
    x, y = point
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y):
            cross_x = (xj - xi) * (y - yi) / ((yj - yi) or 1e-30) + xi
            if x < cross_x:
                inside = not inside
        j = i
    return inside


def point_in_polygon(point, parts):
    if not parts:
        return False
    outer_rings = [ring for ring in parts if len(ring) >= 3]
    if not outer_rings:
        return False
    containing = [ring for ring in outer_rings if point_in_ring(point, ring)]
    if not containing:
        return False
    # Shapefile rings can include holes. The smallest containing ring is the most specific.
    return len(containing) % 2 == 1


def ring_segments(parts, close):
    for ring in parts:
        if len(ring) < 2:
            continue
        for i in range(len(ring) - 1):
            yield ring[i], ring[i + 1]
        if close and len(ring) > 2 and ring[0] != ring[-1]:
            yield ring[-1], ring[0]


def line_segments(parts):
    yield from ring_segments(parts, False)


def nearest_on_segment(point, start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    denom = dx * dx + dy * dy
    t = 0.0 if denom == 0 else max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / denom))
    return start[0] + t * dx, start[1] + t * dy


def segment_intersection(a, b, c, d):
    abx, aby = b[0] - a[0], b[1] - a[1]
    cdx, cdy = d[0] - c[0], d[1] - c[1]
    denom = abx * cdy - aby * cdx
    if abs(denom) < 1e-10:
        return None
    acx, acy = c[0] - a[0], c[1] - a[1]
    t = (acx * cdy - acy * cdx) / denom
    u = (acx * aby - acy * abx) / denom
    if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
        return a[0] + t * abx, a[1] + t * aby
    return None


def closest_segment_points(a, b, c, d):
    intersection = segment_intersection(a, b, c, d)
    if intersection is not None:
        return 0.0, intersection, intersection
    candidates = []
    for point in (a, b):
        other = nearest_on_segment(point, c, d)
        candidates.append((math.dist(point, other), point, other))
    for point in (c, d):
        other = nearest_on_segment(point, a, b)
        candidates.append((math.dist(point, other), other, point))
    return min(candidates, key=lambda item: item[0])


def bbox_overlaps(a, b, padding=0.0):
    return not (
        a[2] < b[0] - padding or a[0] > b[2] + padding
        or a[3] < b[1] - padding or a[1] > b[3] + padding
    )


def segment_bbox(start, end):
    return (
        min(start[0], end[0]),
        min(start[1], end[1]),
        max(start[0], end[0]),
        max(start[1], end[1]),
    )


def grid_cell(x, y):
    return math.floor(x / GRID_SIZE_M), math.floor(y / GRID_SIZE_M)


def grid_cells(bbox, padding=0.0):
    x1, y1, x2, y2 = bbox
    gx1, gy1 = grid_cell(x1 - padding, y1 - padding)
    gx2, gy2 = grid_cell(x2 + padding, y2 + padding)
    for gx in range(gx1, gx2 + 1):
        for gy in range(gy1, gy2 + 1):
            yield gx, gy


def index_logradouros(shapes):
    index = defaultdict(list)
    for i, shape in enumerate(shapes):
        if shape["bbox"] is None or not shape["parts"]:
            continue
        for cell in grid_cells(shape["bbox"]):
            index[cell].append(i)
    return index


def utm25s_to_lonlat(easting, northing):
    # Inverse Transverse Mercator for SIRGAS 2000 / UTM zone 25S.
    a = 6378137.0
    f = 1 / 298.257222101
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    k0 = 0.9996
    x = easting - 500000.0
    y = northing - 10000000.0
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    j1 = 3 * e1 / 2 - 27 * e1**3 / 32
    j2 = 21 * e1**2 / 16 - 55 * e1**4 / 32
    j3 = 151 * e1**3 / 96
    j4 = 1097 * e1**4 / 512
    phi1 = mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu) + j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu)
    sin1 = math.sin(phi1)
    cos1 = math.cos(phi1)
    tan1 = math.tan(phi1)
    n1 = a / math.sqrt(1 - e2 * sin1 * sin1)
    r1 = a * (1 - e2) / (1 - e2 * sin1 * sin1) ** 1.5
    t1 = tan1 * tan1
    c1 = ep2 * cos1 * cos1
    d = x / (n1 * k0)
    lat = phi1 - (n1 * tan1 / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * ep2 - 3 * c1**2) * d**6 / 720
    )
    lon = math.radians(-33.0) + (
        d - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * ep2 + 24 * t1**2) * d**5 / 120
    ) / cos1
    return math.degrees(lon), math.degrees(lat)


def find_neighborhood(center, neighborhood_rows, neighborhood_shapes):
    nearest = (float("inf"), "")
    for row, shape in zip(neighborhood_rows, neighborhood_shapes):
        if shape["bbox"] is None or not shape["parts"]:
            continue
        x, y = center
        x1, y1, x2, y2 = shape["bbox"]
        if x1 <= x <= x2 and y1 <= y <= y2 and point_in_polygon(center, shape["parts"]):
            return row.get("N_BAIRRO", ""), "inside", 0.0
        for start, end in ring_segments(shape["parts"], True):
            point = nearest_on_segment(center, start, end)
            distance = math.dist(center, point)
            if distance < nearest[0]:
                nearest = (distance, row.get("N_BAIRRO", ""))
    if nearest[0] <= 50.0:
        return nearest[1], "near_boundary", nearest[0]
    return "", "unmatched", nearest[0]


def nearby_streets(quad_shape, road_rows, road_shapes, road_grid):
    bbox = quad_shape["bbox"]
    candidates = set()
    for cell in grid_cells(bbox, SEARCH_RADIUS_M):
        candidates.update(road_grid.get(cell, ()))
    quad_edges = list(ring_segments(quad_shape["parts"], True))
    best_by_name = {}
    for index in candidates:
        road_shape = road_shapes[index]
        if road_shape["bbox"] is None or not bbox_overlaps(bbox, road_shape["bbox"], SEARCH_RADIUS_M):
            continue
        name = road_rows[index].get("nome_logr", "").strip()
        if not name:
            continue
        edges = [
            (start, end, segment_bbox(start, end))
            for start, end in line_segments(road_shape["parts"])
        ]
        if not edges:
            continue
        best = None
        for q_start, q_end in quad_edges:
            q_bbox = segment_bbox(q_start, q_end)
            for r_start, r_end, r_bbox in edges:
                if not bbox_overlaps(q_bbox, r_bbox, SEARCH_RADIUS_M):
                    continue
                candidate = closest_segment_points(q_start, q_end, r_start, r_end)
                if best is None or candidate[0] < best[0]:
                    best = candidate
                    if best[0] < 0.01:
                        break
            if best is not None and best[0] < 0.01:
                break
        if best is not None and best[0] <= SEARCH_RADIUS_M:
            current = best_by_name.get(name)
            if current is None or best[0] < current[0]:
                best_by_name[name] = best
    streets = []
    for name, (distance, _quad_point, road_point) in best_by_name.items():
        lon, lat = utm25s_to_lonlat(*road_point)
        streets.append({
            "name": name,
            "distanceMeters": round(distance, 1),
            "latitude": round(lat, 7),
            "longitude": round(lon, 7),
        })
    return sorted(streets, key=lambda item: (item["distanceMeters"], item["name"]))


def main():
    quad_dbf = SOURCE / "quadras" / "quadrasMerge_20261002.dbf"
    quad_shp = SOURCE / "quadras" / "quadrasMerge_20261002.shp"
    road_dbf = SOURCE / "logradouros" / "LOGRADOUROS_ATIVOS.dbf"
    road_shp = SOURCE / "logradouros" / "LOGRADOUROS_ATIVOS.shp"
    bairro_dbf = SOURCE / "bairros" / "bairros.dbf"
    bairro_shp = SOURCE / "bairros" / "bairros.shp"

    quad_rows, quad_shapes = read_dbf(quad_dbf), read_shp(quad_shp)
    road_rows, road_shapes = read_dbf(road_dbf), read_shp(road_shp)
    bairro_rows, bairro_shapes = read_dbf(bairro_dbf), read_shp(bairro_shp)
    if not (len(quad_rows) == len(quad_shapes) and len(road_rows) == len(road_shapes) and len(bairro_rows) == len(bairro_shapes)):
        raise ValueError("DBF and SHP record counts do not match.")
    road_grid = index_logradouros(road_shapes)

    results = []
    for feature_index, (row, shape) in enumerate(zip(quad_rows, quad_shapes), start=1):
        if feature_index % 1000 == 0:
            print(f"Processed {feature_index}/{len(quad_rows)} quadras...", flush=True)
        sector = row.get("setor", "").strip()
        quad = row.get("qd_atual", "").strip()
        if not sector or not quad or shape["bbox"] is None or not shape["parts"]:
            continue
        center = polygon_center(shape["parts"])
        if center is None:
            continue
        neighborhood, neighborhood_method, neighborhood_distance = find_neighborhood(
            center, bairro_rows, bairro_shapes
        )
        if not neighborhood:
            continue
        lon, lat = utm25s_to_lonlat(*center)
        streets = nearby_streets(shape, road_rows, road_shapes, road_grid)
        results.append({
            "id": f"{neighborhood}|{sector.zfill(2)}|{quad.zfill(3)}",
            "neighborhood": neighborhood,
            "neighborhoodMatch": neighborhood_method,
            "sector": sector.zfill(2),
            "quad": quad.zfill(3),
            "center": {"latitude": round(lat, 7), "longitude": round(lon, 7)},
            "streets": streets,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "source": "Filipeia/SEPLAN/PMJP",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "streetSearchRadiusMeters": SEARCH_RADIUS_M,
        "features": results,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(results)} quadras to {OUT}")
    sample = next(
        (item for item in results if item["neighborhood"].upper() == "TORRE" and item["sector"] == "10" and item["quad"] == "119"),
        None,
    )
    print("Sample Torre / Setor 10 / Quadra 119:")
    print(json.dumps(sample, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
