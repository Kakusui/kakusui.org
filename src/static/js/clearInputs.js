function clearElements(elementIds) {
    elementIds.forEach(function(id) {
        var element = document.getElementById(id);
        if (element) {
            element.value = '';
        }
    });
}