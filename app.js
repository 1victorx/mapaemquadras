const DATA_URL = "./data/generated/quadras.json";

function getDailyStorageKey() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return "mapaemquadras.route.v1." + now.getFullYear() + "-" + month + "-" + day;
}

const ROUTE_STORAGE_KEY = getDailyStorageKey();
const form = document.querySelector("#quad-form");
const neighborhoodSelect = document.querySelector("#neighborhood");
const sectorInput = document.querySelector("#sector");
const quadInput = document.querySelector("#quad");
const addButton = document.querySelector("#add-button");
const clearButton = document.querySelector("#clear-button");
const routeList = document.querySelector("#route-list");
const routeCount = document.querySelector("#route-count");
const emptyState = document.querySelector("#empty-state");
const formMessage = document.querySelector("#form-message");
const dataBadge = document.querySelector("#data-badge");
const routeDate = document.querySelector("#route-date");
const officialNeighborhoodButton = document.querySelector("#use-official-neighborhood");

let featureIndex = new Map();
let sectorQuadIndex = new Map();
let routeIds = [];
let suggestedFeature = null;

routeDate.textContent = new Intl.DateTimeFormat("pt-BR", { dateStyle: "full" }).format(new Date());
routeDate.dateTime = new Date().toISOString().slice(0, 10);

function normalizeText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toUpperCase();
}

function numericKey(value, length) {
  const digits = String(value).replace(/\D/g, "");
  return digits.padStart(length, "0");
}

function makeId(neighborhood, sector, quad) {
  return [
    normalizeText(neighborhood),
    numericKey(sector, 2),
    numericKey(quad, 3)
  ].join("|");
}

function makeSectorQuadId(sector, quad) {
  return numericKey(sector, 2) + "|" + numericKey(quad, 3);
}

function loadSavedRoute() {
  try {
    const value = JSON.parse(localStorage.getItem(ROUTE_STORAGE_KEY) || "[]");
    return Array.isArray(value) ? value.filter((item) => typeof item === "string") : [];
  } catch {
    return [];
  }
}

function saveRoute() {
  try {
    localStorage.setItem(ROUTE_STORAGE_KEY, JSON.stringify(routeIds));
    return true;
  } catch {
    setMessage("Não foi possível salvar a rota neste aparelho.", true);
    return false;
  }
}

function hideSuggestion() {
  suggestedFeature = null;
  officialNeighborhoodButton.hidden = true;
  officialNeighborhoodButton.textContent = "";
}

function setMessage(message, isError = false) {
  hideSuggestion();
  formMessage.textContent = message;
  formMessage.classList.toggle("is-error", isError);
}

function titleCase(value) {
  return String(value || "")
    .toLocaleLowerCase("pt-BR")
    .replace(/(^|[\s-])([a-zà-ÿ])/g, (match, gap, letter) => gap + letter.toLocaleUpperCase("pt-BR"))
    .replace(/\b(Da|Das|De|Do|Dos|E)\b/g, (word) => word.toLocaleLowerCase("pt-BR"));
}

function createElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function makeMapsUrl(street) {
  if (Number.isFinite(street.latitude) && Number.isFinite(street.longitude)) {
    const query = street.latitude + "," + street.longitude;
    return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(query);
  }
  return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(street.name + ", João Pessoa, PB");
}

function renderStreet(street, feature) {
  const row = createElement("li", "street-row");
  const name = createElement("span", "street-name", titleCase(street.name));
  const link = createElement("a", "maps-link", "Abrir no Maps");
  link.href = makeMapsUrl(street);
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.setAttribute("aria-label", "Abrir " + titleCase(street.name) + " no Google Maps, perto da quadra " + feature.quad);
  const arrow = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  arrow.setAttribute("viewBox", "0 0 20 20");
  arrow.setAttribute("aria-hidden", "true");
  arrow.innerHTML = '<path d="M5 15 15 5M7 5h8v8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path>';
  link.replaceChildren(createElement("span", "", "Abrir no Maps"), arrow);
  row.append(name, link);
  return row;
}

function renderRoute() {
  routeList.replaceChildren();
  const validItems = routeIds.map((id) => featureIndex.get(id)).filter(Boolean);
  const missingItems = routeIds.filter((id) => !featureIndex.has(id));

  validItems.forEach((feature, index) => {
    const item = createElement("li", "route-stop");
    const header = createElement("div", "stop-heading");
    const order = createElement("span", "stop-order", String(index + 1).padStart(2, "0"));
    order.setAttribute("aria-hidden", "true");

    const titleGroup = createElement("div", "stop-title-group");
    const title = createElement("h3", "stop-title", "Quadra " + feature.quad);
    const meta = createElement("p", "stop-meta", titleCase(feature.neighborhood) + " · Setor " + feature.sector);
    titleGroup.append(title, meta);

    const remove = createElement("button", "remove-button", "Remover");
    remove.type = "button";
    remove.setAttribute("aria-label", "Remover quadra " + feature.quad + " do setor " + feature.sector + " de " + titleCase(feature.neighborhood));
    remove.addEventListener("click", () => {
      const featureId = makeId(feature.neighborhood, feature.sector, feature.quad);
      routeIds = routeIds.filter((id) => id !== featureId);
      const saved = saveRoute();
      renderRoute();
      if (saved) setMessage("Quadra removida da rota.");
    });

    header.append(order, titleGroup, remove);
    item.append(header);

    if (feature.neighborhoodMatch === "near_boundary") {
      item.append(createElement("p", "boundary-note", "Esta quadra fica perto da divisa de bairro; confira o ponto no mapa."));
    }

    if (feature.streets && feature.streets.length) {
      const streetHeading = createElement("p", "street-heading", "Ruas próximas");
      const streets = createElement("ul", "street-list");
      feature.streets.forEach((street) => streets.append(renderStreet(street, feature)));
      item.append(streetHeading, streets);
    } else {
      item.append(createElement("p", "no-streets", "Não encontrei uma rua próxima na base oficial. Confira esta quadra no Filipeia."));
    }

    routeList.append(item);
  });

  missingItems.forEach((id) => {
    routeIds = routeIds.filter((savedId) => savedId !== id);
  });
  if (missingItems.length) saveRoute();

  const count = validItems.length;
  routeCount.textContent = count + (count === 1 ? " quadra" : " quadras");
  emptyState.hidden = count > 0;
  clearButton.hidden = count === 0;
}

function enableForm(neighborhoods) {
  neighborhoodSelect.replaceChildren(new Option("Selecione o bairro", ""));
  neighborhoods.forEach((name) => {
    neighborhoodSelect.add(new Option(titleCase(name), name));
  });
  neighborhoodSelect.disabled = false;
  sectorInput.disabled = false;
  quadInput.disabled = false;
  addButton.disabled = false;
  dataBadge.textContent = "Base disponível";
  dataBadge.classList.add("is-ready");
}

function addFeatureToRoute(feature) {
  const id = makeId(feature.neighborhood, feature.sector, feature.quad);
  if (routeIds.includes(id)) {
    setMessage("Essa quadra já está na rota.");
    neighborhoodSelect.focus();
    return;
  }
  routeIds.push(id);
  const saved = saveRoute();
  renderRoute();
  form.reset();
  neighborhoodSelect.focus();
  if (saved) setMessage("Quadra " + feature.quad + " adicionada à rota.");
}

function showDataMismatch(selectedNeighborhood, feature) {
  const officialNeighborhood = titleCase(feature.neighborhood);
  formMessage.textContent = "Na base municipal, setor " + feature.sector + " / quadra " + feature.quad + " consta em " + officialNeighborhood + ", não em " + titleCase(selectedNeighborhood) + ".";
  formMessage.classList.add("is-error");
  suggestedFeature = feature;
  officialNeighborhoodButton.textContent = "Adicionar como " + officialNeighborhood;
  officialNeighborhoodButton.hidden = false;
}

async function initialize() {
  routeIds = loadSavedRoute();
  try {
    const response = await fetch(DATA_URL, { cache: "no-cache" });
    if (!response.ok) throw new Error("Não consegui carregar o arquivo de dados.");
    const data = await response.json();
    const features = Array.isArray(data.features) ? data.features : [];

    featureIndex = new Map();
    sectorQuadIndex = new Map();
    features.forEach((feature) => {
      const id = makeId(feature.neighborhood, feature.sector, feature.quad);
      featureIndex.set(id, feature);
      const pairId = makeSectorQuadId(feature.sector, feature.quad);
      const matchingPair = sectorQuadIndex.get(pairId) || [];
      matchingPair.push(feature);
      sectorQuadIndex.set(pairId, matchingPair);
    });

    const neighborhoods = Array.from(new Set(features.map((feature) => feature.neighborhood).filter(Boolean)))
      .sort((a, b) => a.localeCompare(b, "pt-BR"));
    enableForm(neighborhoods);
    renderRoute();
    setMessage(features.length.toLocaleString("pt-BR") + " quadras disponíveis para consulta.");
  } catch {
    dataBadge.textContent = "Base indisponível";
    dataBadge.classList.add("is-error");
    setMessage("Não consegui carregar a base de quadras. Confira se o app foi aberto pelo servidor local.", true);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  hideSuggestion();

  const neighborhood = neighborhoodSelect.value;
  const sector = sectorInput.value.trim();
  const quad = quadInput.value.trim();
  if (!neighborhood || !sector || !quad) {
    setMessage("Preencha bairro, setor e quadra.", true);
    return;
  }
  if (!/^\d{1,2}$/.test(sector) || !/^\d{1,3}$/.test(quad)) {
    setMessage("Use apenas números: setor com até 2 dígitos e quadra com até 3.", true);
    return;
  }

  const id = makeId(neighborhood, sector, quad);
  const feature = featureIndex.get(id);
  if (feature) {
    addFeatureToRoute(feature);
    return;
  }

  const alternatives = sectorQuadIndex.get(makeSectorQuadId(sector, quad)) || [];
  if (alternatives.length === 1) {
    showDataMismatch(neighborhood, alternatives[0]);
    return;
  }
  if (alternatives.length > 1) {
    const neighborhoodsFound = Array.from(new Set(alternatives.map((item) => titleCase(item.neighborhood)))).join(", ");
    setMessage("Setor " + sector + " / quadra " + quad + " aparece em mais de um bairro: " + neighborhoodsFound + ". Confira a ordem de serviço.", true);
    return;
  }
  setMessage("Não encontrei essa combinação na base municipal. Confira bairro, setor e número da quadra.", true);
});

officialNeighborhoodButton.addEventListener("click", () => {
  if (!suggestedFeature) return;
  const feature = suggestedFeature;
  addFeatureToRoute(feature);
});

clearButton.addEventListener("click", () => {
  if (!window.confirm("Limpar todas as quadras desta rota?")) return;
  routeIds = [];
  const saved = saveRoute();
  renderRoute();
  if (saved) setMessage("A rota foi limpa.");
  neighborhoodSelect.focus();
});

initialize();
