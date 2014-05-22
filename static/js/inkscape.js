
function getPng(t) {
  if(t.src.slice(-3)=='svg') {
    t.src = t.src.slice(0,-3) + "png";
  }
}

