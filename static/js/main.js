var header = document.getElementById("header");

function headerScroll() {
  if (window.pageYOffset > 0) {
    header.classList.add("header-fixed");
  } else {
    header.classList.remove("header-fixed");
  }
}
