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