import 'lazysizes';
import 'lazysizes/plugins/native-loading/ls.native-loading';



import {
  Alert, 
  Button, 
  // Carousel, 
  // Collapse, 
  // Dropdown, 
  // Modal, 
  // Offcanvas, 
  // Popover, 
  // ScrollSpy, 
  // Tab, 
  // Toast, 
  // Tooltip
} from 'bootstrap';

import {gsap} from 'gsap';
import CSSRulePlugin from 'gsap/CSSRulePlugin';
import { DrawSVGPlugin } from './DrawSVGPlugin';
import { ScrollTrigger } from 'gsap/ScrollTrigger';




//lazySizes native loading
lazySizes.cfg.nativeLoading = {
  setLoadingAttribute: true,
  disableListeners: {
    scroll: true
  },
}

btn_burger.addEventListener('click', () => document.body.classList.toggle('menu_show'))


gsap.registerPlugin(DrawSVGPlugin, ScrollTrigger);

gsap.config({
  nullTargetWarn: false,
  trialWarn: false,
});



ScrollTrigger.defaults({
  toggleActions: 'restart pause resume pause',
  scroller: 'body'
});


// Connectors

const scaleOptions = {
  duration: 1,
  scale: 0,
  transformOrigin: 'center center',
  opacity: 0
}

gsap.timeline({scrollTrigger: '.connectors'})
  .from('.left_part', scaleOptions)
  .from('.right_part', scaleOptions)
  


// automated animation 


const stepProgress = '.text__progress';

const activeStep = () => ({
  duration: gsap.utils.random(0.5, 4),
  width: '100%',
  clipPath: 'inset(-1px 0% -1px 0px)'
})

const automatedPath = {
  duration: 2,
  ease: 'none'
}

gsap.timeline({scrollTrigger: '.automated'})
  .fromTo('#maskPath', {
    drawSVG: 0,
  },
  { 
    ...automatedPath,
    drawSVG: '40%'
    
  })
  .to(`.animation--text__1 ${stepProgress}`, activeStep())
  .to('#maskPath', {
      ...automatedPath,
      drawSVG: '75%'
    })

  .to(`.animation--text__2 ${stepProgress}`, activeStep())
  .to('#maskPath', {
    ...automatedPath,
    drawSVG: '100%'
  })
  .to(`.animation--text__3 ${stepProgress}`, activeStep())
  

gsap.timeline({scrollTrigger: '.security'})
  .fromTo('#secure-path-1', {
    drawSVG: '0%',
  },
  { 
    duration: 3,
    ease: 'none',
    drawSVG: '100%'
  })
  .fromTo('#secure-shield', {
    filter: 'grayscale(1)',
    opacity: 0,
    yPercent: 50
  }, {
    duration: 3,
    filter: 'grayscale(0)',
    yPercent: 0,
    opacity: 1
  }, '-=3')
  .fromTo('#secure-path-2', {
    drawSVG: '0%',
  },
  { 
    duration: 2,
    ease: 'none',
    drawSVG: '100%'
  })

// const secureWave = document.querySelectorAll('.secure-wave');
document.querySelectorAll('.secure-wave')?.forEach((wave) => {
  const randomTime = gsap.utils.random(2, 4);
  gsap.timeline({repeat: -1})
    .set(wave, {
      opacity: 0,
      yPercent: 30,
      ease: "none"
    })
    .to(wave, {
      opacity: 1,
      yPercent: -30,
      duration: randomTime,
      ease: "none"
    })
    .to(wave, {
      opacity: 0,
      yPercent: -70,
      duration: randomTime,
      ease: "none"
    })
})


// console.clear();


const btnDocs = document.getElementById('btnDocs')

btnDocs?.addEventListener('click', function() {
  menuDocs?.classList.toggle('show');
  this?.classList.toggle('active');
});

const formEmail = document.getElementById('email-form')

formEmail?.addEventListener('submit', (event) => {
  let submitter = document.getElementById(event.submitter.id);
  submitter.style.backgroundColor = '#198754';
  submitter.style.borderColor = '#198754';
})

document.querySelectorAll('.dropdown_toggle').forEach( button => {
  button.addEventListener('click', (e) => {
    console.log("test");
    const item = button.closest('.docs__nav--dropdown');
    console.log(item);
    item?.classList.toggle('show');
  })
});




(() => {
  function createLi(title, id) {
    const li = document.createElement('li');  
          li.className = 'toc__nav--item';
    const a = document.createElement('a');  
          a.className = 'toc__nav--anchor';
          a.textContent = title;
          a.href = `#${id}`
    li.append(a);
    return {li, a};
  }

  function addActiveToc(id) {
    const el = document.querySelector('[href="#' + id + '"]');
    el?.closest('.toc__nav--item').classList.add('toc-active');
  }

  function clearActiveToc() {
    document.querySelectorAll('.toc-active')?.forEach((section) => {
      section.classList.remove('toc-active');
    });
  }

  function updateTOC(element) {
    const id = element[0].target.id;
    clearActiveToc()
    addActiveToc(id)
  }

  function createTOC(contentDiv) {

    const titles = document.querySelectorAll(contentDiv + ' h2');

    const ul = document.createElement('ul');
          ul.classList = 'toc__nav';

    let observer = new IntersectionObserver(updateTOC, {
      rootMargin: "0px 0px -70% 0px",
      threshold: 0.5
    });


    ( titles.length > 0 ) && titles?.forEach( anchor => {
      // creates nav items
      const {li, a}  = createLi(anchor.textContent, anchor.id);

      ul.append(li)
      toc_nav.append(ul);

      // scroll to anchor on click
      a.addEventListener('click',(e) => {
        e.preventDefault();
        const offsetTop = anchor.offsetTop;
        scroll({
          top: anchor.offsetTop - 90,
          behavior: "smooth"
        })
      })
      // check position of the titles
      observer.observe(anchor);
    })
  }
  
  createTOC('#doc_content');

})();

async function postFormDataAsJson({ url, formData }) {
	const plainFormData = Object.fromEntries(formData.entries());
	const formDataJsonString = JSON.stringify(plainFormData);

	const fetchOptions = {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		body: formDataJsonString,
	};

	const response = await fetch(url, fetchOptions);

	if (!response.ok) {
		const errorMessage = await response.text();
		throw new Error(errorMessage);
	}

	return response.json();
}

async function handleFormSubmit(event) {
	event.preventDefault();

	const form = event.currentTarget;
	const url = form.action;

	try {
		const formData = new FormData(form);
		const responseData = await postFormDataAsJson({ url, formData });

		console.log({ responseData });
	} catch (error) {
		console.error(error);
	}
}

const exampleForm = document.getElementById("email-form");
exampleForm.addEventListener("submit", handleFormSubmit);
