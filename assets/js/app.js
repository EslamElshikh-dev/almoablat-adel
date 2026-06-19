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

const form = document.getElementById('contactForm');

if(form){

form.addEventListener('submit', function(e){

e.preventDefault();

const name = document.getElementById('name').value;
const phone = document.getElementById('phone').value;
const service = document.getElementById('service').value;
const details = document.getElementById('details').value;

const message =
`الاسم: ${name}
رقم الجوال: ${phone}
الخدمة المطلوبة: ${service}
التفاصيل: ${details}`;

window.open(
`https://wa.me/966567372527?text=${encodeURIComponent(message)}`,
'_blank'
);

});

}
```
