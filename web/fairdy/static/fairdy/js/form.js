function refreshFields() {
    let code = $('#id_code_type > option:selected').val();
    resetAttributes();
    switch(code) {
        case 'REP':
            refreshREP();
            break;
        case 'RS':
            refreshRS();
            break;
        case 'GP':
            refreshGP();
            break;
        case '':
            $('.gpc-fields').hide();
            break;
    }
    let num_stripes = parseInt($('#id_num_stripes').val());
    let blocks_per_stripe = parseInt($('#id_n_value').val());
    let blocks_in_system = num_stripes * blocks_per_stripe;
    $('#id_blocks_in_system').val(blocks_in_system);
    refreshStorageLocations(blocks_in_system);
}

function refreshStorageLocations(blocks_in_system) {
    if ($('#id_storage_location_mode > option:selected').val() == '') {
        $('#id_num_storage_locations').attr('readonly', true);
        $('#id_num_storage_locations').val(blocks_in_system);
    } else {
        $('#id_num_storage_locations').removeAttr('readonly');
    }
}

function resetAttributes() {
    let elements = ['#id_n_value', '#id_m_value', '#id_k_value'];
    elements.forEach(function(element, index){
        $(element).removeAttr('readonly');
        $(element).removeAttr('data-content');
        $(element).removeAttr('title');
    });
}

function refreshRS() {
    $('.gpc-fields').hide();
    let m_val = parseInt($('#id_m_value').val());
    let k_val = parseInt($('#id_k_value').val())
    let n_val = m_val + k_val;

    $('#id_k_value').attr('data-content', '<img src="/web/static/fairdy/rs_k.svg">');
    $('#id_k_value').attr('title', 'The number of equally sized data blocks per stripe');

    $('#id_m_value').attr('data-content', '<img src="/web/static/fairdy/rs_m.svg">');
    $('#id_m_value').attr('title', 'The number of equally sized redundancy blocks per stripe');

    $('#id_n_value').val(n_val);
    $('#id_n_value').attr('readonly', true);
}

function refreshREP() {
    $('.gpc-fields').hide();
    let n_val = parseInt($('#id_m_value').val()) + 1;

    $('#id_n_value').val(n_val);
    $('#id_n_value').attr('readonly', true);

    $('#id_m_value').attr('data-content', 'The number of copies of the single data block to include in the stripe');

    $('#id_k_value').val(1);
    $('#id_k_value').attr('readonly', true);
}

function refreshGP() {
    $('.gpc-fields').show();
    refreshGpcOverlap();

    $('#id_n_value').attr('data-content', '<img src="/web/static/fairdy/gpc.svg">');
    $('#id_n_value').attr('title', 'This stripe has 20 blocks');

    $('#id_m_value').attr('readonly', true);

    $('#id_k_value').attr('readonly', true);

}

//function to check if the defined GPC stripe is overlapping or not
function refreshGpcOverlap() {
    let k_hor = parseInt($('#id_k_horizontal').val());
    let m_hor = parseInt($('#id_m_horizontal').val());
    let k_ver = parseInt($('#id_k_vertical').val());
    let m_ver = parseInt($('#id_m_vertical').val());
    let n_val = parseInt($('#id_n_value').val());
    let rect_size = ((k_hor+m_hor) * (k_ver+m_ver));
    //check for overlapping pyramid simulation
    if (rect_size == n_val) {
        //overlapping
        $('#radio_nonoverlapping').attr('checked', false);
        $('#radio_overlapping').attr('checked', true);
        $('#id_n_value').val(n_val);
        $('#id_k_value').val(k_hor*k_ver);
        $('#id_m_value').val(n_val - (k_hor*k_ver));
    } else {
        //non-overlapping
        $('#radio_overlapping').attr('checked', false);
        $('#radio_nonoverlapping').attr('checked', true);
        $('#id_n_value').val(n_val);
        $('#id_k_value').val(k_hor*k_ver);
        $('#id_m_value').val(m_hor*k_ver + k_hor*m_ver);
    }
}
