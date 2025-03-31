console.log("main.js loaded");
import { Streamlit } from "streamlit-component-lib";

const precisionMap = {
  BTC: 5, ETH: 4, XRP: 3, ADA: 3, SOL: 5, LINK: 3,
  ONDO: 3, CRV: 3, CVX: 3, SUI: 3, FARTCOIN: 3,
};

let asset = "BTC";
let position = 500;
let leverage = 20;
let entry = 82000;
let stop = 81000;
let target = 83000;
let livePrice = null;

const digits = () => precisionMap[asset] || 2;

function format(value) {
  return Number(value).toFixed(digits());
}

function calculate() {
  const total = position * leverage;
  const risk = Math.abs(entry - stop) * total / entry;
  const reward = Math.abs(target - entry) * total / entry;
  const breakeven = ((entry + stop) / 2).toFixed(digits());
  const rr = (reward / risk).toFixed(2);

  document.getElementById("output").innerHTML = `
    <p><strong>Live Price:</strong> $${livePrice ?? "N/A"}</p>
    <p><strong>Total Exposure:</strong> £${total}</p>
    <p><strong>Risk:</strong> £${risk.toFixed(2)}</p>
    <p><strong>Reward:</strong> £${reward.toFixed(2)}</p>
    <p><strong>Breakeven:</strong> ${breakeven}</p>
    <p><strong>RR Ratio:</strong> ${rr}:1</p>
  `;

  Streamlit.setComponentValue({ asset, entry, stop, target, risk, reward, rr });
}

function updateField(id, value) {
  if (id === "asset") asset = value;
  else if (id === "position") position = +value;
  else if (id === "leverage") leverage = +value;
  else if (id === "entry") entry = +value;
  else if (id === "stop") stop = +value;
  else if (id === "target") target = +value;
  calculate();
}

function render() {
  const root = document.getElementById("root");
  root.innerHTML = `
    <div class="p-4 bg-gray-900 text-white rounded-2xl shadow-md max-w-xl mx-auto space-y-4 border border-yellow-500">
      <h2 class="text-xl font-bold text-yellow-400">[DEBUG] Component loaded</h2>
      <h2 class="text-xl font-bold text-blue-400">PnL Calculator</h2>
      <div class="flex gap-2 flex-wrap">
        ${Object.keys(precisionMap).map(a => `
          <button onclick="updateField('asset', '${a}')" class="px-3 py-1 rounded-full ${asset === a ? "bg-blue-500 text-white" : "bg-gray-700"}">${a}</button>
        `).join("")}
      </div>
      <div class="grid grid-cols-2 gap-4">
        ${["Position (£)", "Leverage", "Entry", "Stop Loss", "Take Profit"].map((label, i) => {
          const ids = ["position", "leverage", "entry", "stop", "target"];
          const values = [position, leverage, entry, stop, target];
          return `
            <label>${label}
              <input type="number" value="${values[i]}" oninput="updateField('${ids[i]}', this.value)" class="w-full border rounded p-1 text-black" />
            </label>
          `;
        }).join("")}
      </div>
      <div id="output" class="mt-4 bg-gray-800 p-4 rounded-lg text-sm space-y-1"></div>
    </div>
  `;
  calculate();
}

async function init() {
  try {
    const res = await fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${asset.toLowerCase()}&vs_currencies=usd`);
    const data = await res.json();
    const price = data[asset.toLowerCase()]?.usd;
    if (price) {
      livePrice = format(price);
      entry = +price;
    }
  } catch {
    livePrice = "N/A";
  }
  render();
  Streamlit.setComponentReady();
  Streamlit.setFrameHeight();
}

init();
