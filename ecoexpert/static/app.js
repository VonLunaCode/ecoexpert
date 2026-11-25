'use strict';
const $ = (s) => document.querySelector(s);
const examples = {
  fruta:{objeto:'restos_comida',limpio:null,contacto_quimicos:'no'},
  botella:{objeto:'botella_plastico',limpio:'si',contacto_quimicos:'no'},
  celular:{objeto:'celular',limpio:null,contacto_quimicos:'no'},
  contacto:{objeto:'lata',limpio:'no',contacto_quimicos:'si'}
};
let busy=false,hasResult=false,revision=0;
function dependencies(){
  const relevant=['botella_plastico','caja_carton','hojas_papel','frasco_vidrio','lata'].includes($('#objeto').value);
  $('#clean-field').hidden=!relevant;
  if(!relevant)$('#limpio').value='desconocido';
}
function changed(){revision++;dependencies();if(hasResult)$('#stale').hidden=false;}
$('#consulta').addEventListener('change',changed);
document.querySelectorAll('[data-example]').forEach(button=>button.addEventListener('click',()=>{
  if(busy)return;
  const example=examples[button.dataset.example];
  $('#objeto').value=example.objeto;
  $('#limpio').value=example.limpio||'desconocido';
  $('#contacto').value=example.contacto_quimicos;
  changed();
}));
$('#consulta').addEventListener('reset',()=>{
  revision++;hasResult=false;$('#clean-field').hidden=true;$('#empty').hidden=false;$('#answer').hidden=true;$('#error').hidden=true;
});
async function json(url,options={}){
  const response=await fetch(url,{...options,signal:AbortSignal.timeout(12000)});
  if(!response.ok)throw new Error('Revisa las respuestas y vuelve a intentarlo.');
  if(!response.headers.get('content-type')?.includes('application/json'))throw new Error('La respuesta no es válida. Inténtalo de nuevo.');
  return response.json();
}
$('#consulta').addEventListener('submit',async event=>{
  event.preventDefault();if(busy)return;
  const revisionSent=revision;
  const datos={objeto:$('#objeto').value,limpio:$('#clean-field').hidden?null:$('#limpio').value,contacto_quimicos:$('#contacto').value};
  busy=true;$('#evaluate').disabled=true;$('#evaluate').textContent='Clasificando…';$('#error').hidden=true;
  try{
    const result=await json('/api/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(datos)});
    if(revision!==revisionSent)return;
    hasResult=true;$('#empty').hidden=true;$('#answer').hidden=false;$('#stale').hidden=true;
    $('#title').textContent=result.titulo;$('#recommendation').textContent=result.recomendacion;$('#trace').replaceChildren();
    for(const paso of result.pasos){const li=document.createElement('li'),strong=document.createElement('strong');strong.textContent=paso.id;li.append(strong,document.createTextNode(paso.entonces));$('#trace').append(li);}
    if(!result.pasos.length){const li=document.createElement('li');li.textContent='No hay una regla suficiente para este objeto.';$('#trace').append(li);}
    if(matchMedia('(max-width:700px)').matches)$('#answer').scrollIntoView({block:'start',behavior:'auto'});
  }catch(error){$('#error').textContent=error.message==='Revisa las respuestas y vuelve a intentarlo.'?error.message:'No se pudo conectar. Tus respuestas siguen aquí; vuelve a intentarlo.';$('#error').hidden=false;}
  finally{busy=false;$('#evaluate').disabled=false;$('#evaluate').textContent='Clasificar residuo';}
});
json('/api/rules').then(reglas=>{
  for(const regla of reglas){const li=document.createElement('li');li.textContent=`${regla.id}. Si: ${regla.si} Entonces: ${regla.entonces}`;$('#rule-list').append(li);}
}).catch(()=>{$('#rule-list').textContent='No se pudieron cargar las reglas. Recarga la página.';});
