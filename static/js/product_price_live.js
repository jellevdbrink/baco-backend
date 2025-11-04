(function() {
  function updatePricePreview() {
    const costInput = document.getElementById("id_cost_ex_btw");
    const packSizeInput = document.getElementById("id_pack_size");
    const btwInput = document.getElementById("id_btw");

    const previewEl = document.getElementById("price-preview");
    if (!previewEl || !costInput || !packSizeInput || !btwInput) return;

    const cost = parseFloat(costInput.value) || 0;
    const packSize = parseInt(packSizeInput.value) || 1;
    const btw = parseFloat(btwInput.value) || 9;
    const margin = parseFloat(previewEl.dataset.margin) || 1.1;

    const btwMultiplier = 1 + btw / 100;
    const unitCost = (cost * btwMultiplier) / packSize;
    const newPrice = unitCost * margin;

    const rounded = Math.round(newPrice / 0.05) * 0.05;

    previewEl.textContent = `€${rounded.toFixed(2)}`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    ["id_cost_ex_btw", "id_pack_size", "id_btw"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", updatePricePreview);
    });
    updatePricePreview();
  });
})();