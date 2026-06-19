window.addEventListener('scroll', () => {

const header = document.querySelector('.header');

if(window.scrollY > 50){

header.style.background = 'rgba(255,255,255,.12)';
header.style.backdropFilter = 'blur(20px)';

}else{

header.style.background = 'rgba(255,255,255,.35)';
header.style.backdropFilter = 'blur(12px)';

}

});
```javascript
const observer = new IntersectionObserver((entries)=>{

entries.forEach((entry)=>{

if(entry.isIntersecting){

entry.target.classList.add('show');

}

});

},{
threshold:0.15
});

document.querySelectorAll('.feature-box').forEach((box)=>{

observer.observe(box);

});
```
