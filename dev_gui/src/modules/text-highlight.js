function textHighlight() {
  const highlight = (CSS.highlights) ? new Highlight() : null;

  function applyTo(item, start, end) {
    if (highlight) {
      const textnode = item.textNode;
      const range = new Range();
      range.setStart(textnode, start);
      range.setEnd(textnode, end);
      highlight.add(range);
    }
  }
  return {
    applyTo
  }
}
const TextHighlight = textHighlight();
export {
  TextHighlight
};