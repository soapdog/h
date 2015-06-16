module.exports = ->
  link: (scope, elem, attr, ctrl) ->
    scope.$evalAsync -> if elem[0].scrollHeight > elem[0].clientHeight
      elem.prepend angular.element '<span class="more"> More...</span>'
      elem.append angular.element '<span class="less"> Less ^</span>'
      elem.find('.more').on 'click', ->
        $(this).hide()
        elem.addClass('show-full-excerpt')
      elem.find('.less').on 'click', ->
        elem.find('.more').show()
        elem.removeClass('show-full-excerpt')
  restrict: 'C'
