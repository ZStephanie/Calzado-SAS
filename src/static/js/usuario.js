const sideMenu = document.querySelector('aside');
const menuBtn = document.querySelector('#menu_bar');
const closeBtn = document.querySelector('#close_btn');
const themeToggler = document.querySelector('.theme-toggler');
const themeImage = document.getElementById('themeImage')

menuBtn.addEventListener('click', ()=>{
    sideMenu.style.display ="block"
})
closeBtn.addEventListener('click', ()=>{
    sideMenu.style.display ="none"
})

themeToggler.addEventListener('click', () => {
    const isDark = document.body.classList.toggle('dark-theme-variables');
    
    themeToggler.querySelector('span:nth-child(1)').classList.toggle('active', !isDark);
    themeToggler.querySelector('span:nth-child(2)').classList.toggle('active', isDark);

    if (isDark) {
        themeImage.src = '/static/img/CALZADO_SAS_BLANCO.png';
    } else {
        themeImage.src = '/static/img/CALZADO_SAS.png';
    }
});