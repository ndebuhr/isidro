import 'lazysizes';
import 'lazysizes/plugins/native-loading/ls.native-loading';

import {gsap} from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';


// lazySizes native loading
lazySizes.cfg.nativeLoading = {
  setLoadingAttribute: true,
  disableListeners: {
    scroll: true
  },
}

btn_burger.addEventListener('click', () => document.body.classList.toggle('menu_show'))


gsap.registerPlugin(ScrollTrigger);

gsap.config({
  nullTargetWarn: false,
  trialWarn: false,
});



ScrollTrigger.defaults({
  toggleActions: 'restart pause resume pause',
  scroller: 'body'
});


// connectors

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
gsap.utils.toArray(".animation").forEach(section => {
  const wrapper = section.querySelector('.animation--scroller');
  const inner = section.querySelector('.animation--inner');

  const items = section.querySelectorAll('.animation__item');

	let tl = gsap.timeline({
			scrollTrigger: {
				trigger: section,
				start: "bottom bottom",
        // makes the height of scrolling (while pinning) match the width, so that the speed remains constant (vertical/horizontal)
				end: () => "+=" + inner.scrollHeight, 
				pin: true,
        anticipatePin: 1,
        scrub: 1
			},
      defaults: { 
        duration: 1, 
        ease:'none'
      }
		});
    
  tl.to(inner, {y: -(inner.scrollHeight -  wrapper.offsetHeight / 2  ) });

  gsap.utils.toArray(items).forEach( item => {

    const inner = item.children;

    let itemTL = gsap.timeline({
      scrollTrigger: {
        trigger: item,
        start: "center 85%",
        end: "top top"
      },
      defaults: { 
        duration: 1, 
        ease:'none'
      }
    })
    itemTL.fromTo( inner , { opacity: 0 }, {opacity: 1} );
  });
});




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

