const sidebar = document.querySelector(".sidebar");
function showSidebar()
{
    sidebar.style.display = "flex";
}
function closeSidebar()
{
    sidebar.style.display = "none";
}
window.addEventListener('resize', function() {
    const sidebar = document.querySelector('.sidebar');
    if (window.innerWidth > 800 && sidebar.style.display === 'flex') {
        closeSidebar();
    }
});

document.querySelectorAll('ul > li').forEach(function(parentLi) {
    parentLi.addEventListener('click', function() {
      
      this.classList.toggle('open');
      
      event.stopPropagation();
    });
  });