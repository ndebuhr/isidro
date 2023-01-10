// custom select function
const formFeedback = document.getElementById('feedback__form');
const customRadio = document.querySelectorAll('.feedback__form--radio__custom--input');
const formFeedbackAlert = document.querySelector('.feedback__form--submit__alert');

customRadio.forEach( input =>  {
  const inputRadio = input.closest('label').firstElementChild;
  input.oninput = function () {
    this.parentNode.dataset.value = this.value;
    inputRadio.value = this.value;
  }
  input.onfocus = function () {
    inputRadio.checked = true;
  }
})


function disableForm (form, type) {
  const elements = form.querySelectorAll('input, select, textarea, button');
  elements.forEach( element => {
    element.disabled = type ? true : false;
  })
}

function validateFields (form) {
  const elements = form.querySelectorAll('textarea[required]');
  elements.forEach(element => {
   if(element.value.length < 1) {
    element.classList.add("error");
   } else {
    element.classList.remove("error");
   }
  })
}


window.submitFeedback = async (e) => {

  const URL = '/v1/feedback';

  if (!formFeedback.checkValidity()) {
    grecaptcha.reset();
    formFeedback.reportValidity();
    validateFields(formFeedback);
    return
  } else {
    validateFields(formFeedback);
  }

  // loading element
  disableForm(formFeedback, true);
  formFeedback.classList.add('loading');

  // form data
  const type = formFeedback.elements['user_type'],
        role = formFeedback.elements['role'],
        feedbackMessage = formFeedback.elements['feedbackMessage'];


  const data = {
    user_type: type.value,
    user_role: role.value,
    feedback_message: feedbackMessage.value
  }

  const response = await fetch(URL, {
    method: 'POST',
    body: JSON.stringify(data)
  });

  formFeedback.classList.remove('loading');
  
  if (!response.ok) {
    formFeedback.classList.add('error');
    disableForm(formFeedback, false);
    return 
  }

  formFeedback.classList.remove('error');
  formFeedbackAlert.innerText = 'Thanks for your feedback!'
  formFeedback.classList.add('success');
}









