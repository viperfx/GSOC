(function ($) {

  window.MGM = window.MGM || {};
  MGM.translate = {
    init: function() {
        // console.log($("#targetFrame").contents());
        // $("#tabzilla-panel").remove();
        // var URLParams = $.param({
        //   'source': $("#targetFrame").contents()[0].body.innerText,
        // });

        // var queryURL = [
        //   '/tmserver/', 'en', '/', 'es', '/unit/?',
        //   URLParams
        // ].join('');
        // $.getJSON(queryURL, MGM.translate.translateFrame);
    },
    translateFrame: function (data) {
      var searchString = $("#targetFrame").contents()[0].body.innerText.toLowerCase();
      // var searchTerms = $("#targetFrame").contents()[0].body.innerText.split("\n");
      if (data.length) {
        var currentResult,
            resultQuality,
            resultString = [];
        //_.map(searchTerms, function(val) { return val.split(" "); });
        // console.log(searchTerms);
        console.table(data);
        var body_html = $("#targetFrame").contents().find("body").html()
        _.each(data, function(el, idx, list) {
          if (searchString.indexOf(el.source.toLowerCase()) >= 0) {
            body_html = body_html.replace(new RegExp(el.source+"(?![^<]*>)", "ig"), el.target);
          }
        });
        $("#targetFrame").contents().find("body").html(body_html);
        // for (var i = 0; i < searchTerms.length; i++) {
        //   for (var j = 0; j < data.length; j++) {
        //     if (searchTerms[i].toLowerCase() == data[j].source.toLowerCase()) {
        //       searchTerms[i] = data[j].target;
        //     }
        //   }
        // }
      } else {
        console.log("no results")
      }
    }
  };
  MGM.search = {

    init: function () {
      $(document).on('submit', '#js-amagama-form', MGM.search.doSearch);
      $.getJSON('/tmserver/languages/', MGM.search.displayLanguages);
      $('#js-search-box').focus();
    },

    doSearch: function (event) {
      event.preventDefault();
      var searchTerms = $('#js-search-box').val();

      // Only trigger the search if query terms have been provided.
      if (searchTerms) {
        //TODO look for a way to specify min_similarity and max_candidates on
        // the search box instead of hardcoding them here.
        var minSimilarity = 30,
            maxCandidates = 20,
            sourceLanguage = $('#js-source-language').val(),
            targetLanguage = $('#js-target-language').val();

        MGM.search.searchTitle = [
          searchTerms, ' (', sourceLanguage, ' → ', targetLanguage, ')'
        ].join('');

        var URLParams = $.param({
          'source': searchTerms,
          'min_similarity': minSimilarity,
          'max_candidates': maxCandidates
        });

        var queryURL = [
          '/tmserver/', sourceLanguage, '/', targetLanguage, '/unit/?',
          URLParams
        ].join('');

        // Query the amaGama API and display the results.
        $.getJSON(queryURL, MGM.search.displayResults);
      }
    },

    displayResults: function (data) {
      $('#js-similar-title').text(MGM.search.searchTitle);
      $('#js-similar-count').text('Found ' + data.length + ' results.');
      var searchTerms = $('#js-search-box').val();
      if (data.length) {
        var currentResult,
            resultQuality,
            resultString = [],
            searchString = searchTerms.split(" ");
        console.log(searchString);
        console.table(data);
        for (var i = 0; i < searchString.length; i++) {
          
          for (var j = 0; j < data.length; j++) {
            if (searchString[i].toLowerCase() == data[j].source.toLowerCase()) {
              searchString[i] = data[j].target;
            }
          }
        }

        $('#js-result-box').text(searchString.join(' '));
      } else {
        console.log("no results")
      }
    },

    populateDropdown: function (languages, $dropdown) {
      var langsHTML = [];

      for (var i = 0; i < languages.length; i++) {
        langsHTML.push('<option value="');
        langsHTML.push(languages[i]);
        langsHTML.push('">');
        langsHTML.push(languages[i]);
        langsHTML.push('</option>');
      }

      $dropdown.html(langsHTML.join(''));
    },

    displayLanguages: function (data) {
      var $sourceLanguage = $('#js-source-language'),
          $targetLanguage = $('#js-target-language'),
          browserLang = navigator.language || navigator.userLanguage;

      MGM.search.populateDropdown(data.sourceLanguages, $sourceLanguage);
      MGM.search.populateDropdown(data.targetLanguages, $targetLanguage);

      $sourceLanguage.find('option[value="en"]').prop('selected', true);
      $targetLanguage.find('option[value="' + browserLang + '"]')
                     .prop('selected', true);
    }
  };

}(jQuery));
