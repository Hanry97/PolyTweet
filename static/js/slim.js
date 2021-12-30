$(function(){
  'use strict';

  // showing 2nd level sub menu while hiding others
  $('.sidebar-nav-link').on('click', function(e){
    var subMenu = $(this).next();

    $(this).parent().siblings().find('.sidebar-nav-sub').slideUp();
    $('.sub-with-sub ul').slideUp();

    if(subMenu.length) {
      e.preventDefault();
      subMenu.slideToggle();
    }
  });

  // showing 3rd level sub menu while hiding others
  $('.sub-with-sub .nav-sub-link').on('click', function(e){
    e.preventDefault();
    $(this).parent().siblings().find('ul').slideUp();
    $(this).next().slideDown();
  });

  $('#slimSidebarMenu').on('click', function(e){
    e.preventDefault();
    if (window.matchMedia('(min-width: 1200px)').matches) {
      $('body').toggleClass('hide-sidebar');
    } else {
      $('body').toggleClass('show-sidebar');
    }
  });

  if($.fn.perfectScrollbar) {
    $('.slim-sidebar').perfectScrollbar({
      suppressScrollX: true
    });
  }

  $('[data-toggle="tooltip"]').tooltip({ trigger: 'hover' });


  /////////////////// START: TEMPLATE SETTINGS /////////////////////


  // toggles header to sticky
  $('body').on('click', '.sticky-header', function(){
    var val = $(this).val();
    if(val === 'yes') {
      $.cookie('sticky-header', 'true');
      $('body').addClass('slim-sticky-header');
    } else {
      $.removeCookie('sticky-header');
      $('body').removeClass('slim-sticky-header');
    }
  });

  // toggles sidebar to sticky
  $('body').on('click', '.sticky-sidebar', function(){
    if($('.slim-sidebar').length) {
      var val = $(this).val();
      if(val === 'yes') {
        $.cookie('sticky-sidebar', 'true');
        $('body').addClass('slim-sticky-sidebar');
      } else {
        $.removeCookie('sticky-sidebar');
        $('body').removeClass('slim-sticky-sidebar');
      }
    } else {
      alert('Can only be used when navigation is set to vertical');
      $('.sticky-sidebar[value="no"]').prop('checked', true);
    }
  });

  // set skin to header
  $('body').on('click', '.header-skin', function(){
    var val = $(this).val();
    if(val !== 'default') {
      $.cookie('header-skin', val);
      $('#headerSkin').attr('href','../css/slim.'+val+'.css');
    } else {
      $.removeCookie('header-skin');
      $('#headerSkin').attr('href', '');
    }
  });

  // set page to wide
  $('body').on('click', '.full-width', function(){
    var val = $(this).val();
    if(val === 'yes') {
      $.cookie('full-width', 'true');
      $('body').addClass('slim-full-width');
    } else {
      $.removeCookie('full-width');
      $('body').removeClass('slim-full-width');
    }
  });

  /////////////////// END: TEMPLATE SETTINGS /////////////////////


});
