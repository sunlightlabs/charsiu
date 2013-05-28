(function() {

var relPosition = function(span) {
    var offset = span.offset();

    var parent = span.parents('.annotator-wrapper');
    var poffset = parent.offset();

    return {'left': (offset.left - poffset.left) + 'px', 'top': (offset.top - poffset.top) + 'px'};
}

// monkey patch the annotator
Annotator.prototype.checkForEndSelection = function(event) {
  var container, range, _k, _len2, _ref1;

  this.mouseIsDown = false;
  if (this.ignoreMouseup) {
    return;
  }
  this.selectedRanges = this.getSelectedRanges();
  _ref1 = this.selectedRanges;
  for (_k = 0, _len2 = _ref1.length; _k < _len2; _k++) {
    range = _ref1[_k];
    container = range.commonAncestor;
    if ($(container).hasClass('annotator-hl')) {
      container = $(container).parents('[class^=annotator-hl]')[0];
    }
    if (this.isAnnotator(container)) {
      return;
    }
  }
  if (event && this.selectedRanges.length) {
    // short-circuit the built-in positioner and use our own
    var selection = window.getSelection();
    var text = selection.toString();
    if (selection.rangeCount==0) return;

    var range = selection.getRangeAt(0);
    var $span= $("<span/>");

    newRange = document.createRange();
    newRange.setStart(selection.focusNode, range.endOffset);
    newRange.insertNode($span[0]); // using 'range' here instead of newRange unselects or causes flicker on chrome/webkit

    var position = relPosition($span);
    $span.remove();

    return this.adder.css(position).show();
  } else {
    return this.adder.hide();
  }
};

Annotator.prototype.onHighlightMouseover = function(event) {
  var annotations;

  this.clearViewerHideTimer();
  if (this.mouseIsDown || this.viewer.isShown()) {
    return false;
  }
  annotations = $(event.target).parents('.annotator-hl').andSelf().map(function() {
    return $(this).data("annotation");
  });
  return this.showViewer($.makeArray(annotations), relPosition($(event.target)));
};

})();