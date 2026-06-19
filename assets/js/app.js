```javascript
window.addEventListener('scroll', () => {

const header = document.querySelector('.header');

if(window.scrollY > 50){

header.style.background = 'rgba(255,255,255,.12)';
header.style.backdropFilter = 'blur(20px)';
header.style.webkitBackdropFilter = 'blur(20px)';

}else{

header.style.background = 'rgba(255,255,255,.35)';
header.style.backdropFilter = 'blur(12px)';
header.style.webkitBackdropFilter = 'blur(12px)';

}

});
```
