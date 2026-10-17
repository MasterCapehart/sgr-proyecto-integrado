document.addEventListener('DOMContentLoaded',()=>{
 const form=document.getElementById('login-form');if(!form)return;
 const user=document.getElementById('username'),pass=document.getElementById('password'),button=document.getElementById('btn-submit');
 document.getElementById('toggle-password')?.addEventListener('click',e=>{pass.type=pass.type==='password'?'text':'password';e.target.textContent=pass.type==='password'?'Mostrar':'Ocultar';e.target.setAttribute('aria-label',pass.type==='password'?'Mostrar contraseña':'Ocultar contraseña');e.target.setAttribute('aria-pressed',String(pass.type==='text'));});
 form.addEventListener('submit',async e=>{e.preventDefault();if(!user.value.trim()||!pass.value){await SGRApi.message('Completa usuario o correo y contraseña.','warning');return;}
 button.disabled=true;button.textContent='Verificando…';
 try{await SGRApi.send('/api/login/',{username:user.value.trim(),password:pass.value});sessionStorage.clear();location.href='../index.html';}catch(ex){await SGRApi.message(ex.message);pass.value='';pass.focus();}finally{button.disabled=false;button.textContent='Ingresar al sistema →';}
 });
});
