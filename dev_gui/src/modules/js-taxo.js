  function TaxoHelperBtAdd() {
    var s = $('#oldname').val() + "=" + $('#taxolb option:selected').text();
    var txt = $('#TxtTaxoMap');
    txt.val(txt.val() + s + "\n");
  }

  $(document).ready(function() {

    $(".taxolb").select2({
      ajax: {
        url: "/search/taxo",
        dataType: 'json',
        delay: 250,
        data: function(params) {
          return {
            q: params.term,
            page: params.page
          };
        },
        processResults: function(data) {
          return {
            results: data
          };
        },
        cache: true
      },
      minimumInputLength: 3
    });
    $('#TaxoModal').on('show.bs.modal', function() {
      $("#FileModalBody").html("");
      $("#TaxoModalBody").html("Loading...").load("/search/taxotree?target=taxolb");
    });
  }); // Ready