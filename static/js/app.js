const bookingForm=document.getElementById('booking-form');
const destinationSelect=document.getElementById('destination');
const customDestinationWrap=document.getElementById('custom-destination-wrap');
const travelersChoice=document.getElementById('travelers-choice');
const groupSizeWrap=document.getElementById('group-size-wrap');
const groupSizeInput=document.getElementById('group-size');
const travelDateInput=document.getElementById('travel-date');
const formStatus=document.getElementById('form-status');
const submitButton=document.getElementById('submit-button');
const modal=document.getElementById('tour-modal');
const modalContent=document.getElementById('tour-modal-content');
const navToggle=document.querySelector('.nav-toggle');
const navLinks=document.getElementById('nav-links');

const today=new Date();
const localToday=new Date(today.getTime()-today.getTimezoneOffset()*60000).toISOString().split('T')[0];
travelDateInput.min=localToday;

navToggle.addEventListener('click',()=>{const isOpen=navLinks.classList.toggle('open');navToggle.setAttribute('aria-expanded',String(isOpen));});
navLinks.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>navLinks.classList.remove('open')));

destinationSelect.addEventListener('change',()=>{
  const showCustom=destinationSelect.value==='Other / Custom Destination';
  customDestinationWrap.classList.toggle('hidden-field',!showCustom);
  const customInput=customDestinationWrap.querySelector('input');
  customInput.required=showCustom;
  if(!showCustom)customInput.value='';
});

travelersChoice.addEventListener('change',()=>{
  const needsGroupSize=travelersChoice.value==='6+';
  groupSizeWrap.classList.toggle('hidden-field',!needsGroupSize);
  groupSizeInput.required=needsGroupSize;
  if(!needsGroupSize)groupSizeInput.value='';
});

function clearErrors(){document.querySelectorAll('.field-error').forEach(el=>el.textContent='');formStatus.className='form-status';formStatus.textContent='';}
function showErrors(errors={}){Object.entries(errors).forEach(([field,message])=>{const target=document.querySelector(`[data-error-for="${field}"]`);if(target)target.textContent=message;});}
function resolveTravelerCount(){return travelersChoice.value==='6+'?Number(groupSizeInput.value||0):Number(travelersChoice.value||0);}

bookingForm.addEventListener('submit',async event=>{
  event.preventDefault();clearErrors();
  const formData=new FormData(bookingForm);
  const payload=Object.fromEntries(formData.entries());
  payload.travelers=resolveTravelerCount();

  if(!bookingForm.reportValidity())return;
  if(!/^\d{10}$/.test(payload.phone||'')){showErrors({phone:'Phone number must contain exactly 10 digits.'});return;}
  if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(payload.email||'')){showErrors({email:'Enter a valid email address.'});return;}
  if(payload.travelers<1||payload.travelers>30){showErrors({travelers:'Travelers must be between 1 and 30.'});return;}

  submitButton.disabled=true;submitButton.textContent='Sending...';
  try{
    const response=await fetch('/api/bookings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const data=await response.json();
    if(!response.ok){showErrors(data.errors||{});throw new Error(data.message||'Unable to submit booking.');}
    formStatus.className='form-status success';
    formStatus.textContent=`Booking received. Reference: ${data.booking_reference}`;
    bookingForm.reset();customDestinationWrap.classList.add('hidden-field');groupSizeWrap.classList.add('hidden-field');travelDateInput.min=localToday;
  }catch(error){formStatus.className='form-status error';formStatus.textContent=error.message||'Something went wrong. Please try again.';}
  finally{submitButton.disabled=false;submitButton.textContent='Book Your Adventure';}
});

function escapeHtml(value){return String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');}
function listItems(items){return items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');}

document.querySelectorAll('.explore-button').forEach(button=>{
  button.addEventListener('click',()=>{
    const tour=JSON.parse(button.dataset.tour);
    modalContent.innerHTML=`
      <div class="modal-hero" style="background-image:linear-gradient(rgba(6,23,45,.12),rgba(6,23,45,.32)),url('${tour.image}')"></div>
      <div class="modal-body">
        <p class="eyebrow">${escapeHtml(tour.state)}</p>
        <h2>${escapeHtml(tour.name)} Adventure</h2>
        <p class="modal-subtitle">${escapeHtml(tour.summary)}</p>
        <div class="modal-stats">
          <div><span>Duration</span><strong>${escapeHtml(tour.duration)}</strong></div>
          <div><span>Starting at</span><strong>${escapeHtml(tour.price)}</strong></div>
          <div><span>Best time</span><strong>${escapeHtml(tour.best_time)}</strong></div>
        </div>
        <div class="modal-lists">
          <div><h3>Activities</h3><ul>${listItems(tour.activities)}</ul></div>
          <div><h3>Package includes</h3><ul>${listItems(tour.includes)}</ul></div>
        </div>
        <button class="button button-full modal-book-button" type="button">Book This Tour</button>
      </div>`;
    modal.showModal();
    modalContent.querySelector('.modal-book-button').addEventListener('click',()=>{
      destinationSelect.value=tour.name;
      destinationSelect.dispatchEvent(new Event('change'));
      modal.close();
      document.getElementById('booking').scrollIntoView({behavior:'smooth',block:'center'});
    });
  });
});

document.querySelector('.modal-close').addEventListener('click',()=>modal.close());
modal.addEventListener('click',event=>{if(event.target===modal)modal.close();});
