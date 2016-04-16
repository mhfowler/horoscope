$(document).ready(function() {

    $(".click-to-delete").click(function(e) {
        var r = confirm("Are you sure you want to turn off this alert?");
        if (r == true) {
            var wrapper = $(this).parents('.alert');
            var phonediv = wrapper.find('.phone');
            var fbdiv = wrapper.find('.fblink');
            $.post("/remove_alert/", {
                phone: phonediv.data('phone'),
                fblink: fbdiv.data('fblink')
            }, function (data) {
                location.reload();
            });
        }
    });

    $(".set-new-alert-button").click(function(e) {
        var phone = $('.phone-input').val();
        var fblink = $('.fb-input').val();
        var provider = $('input[name=provider]:checked').val();
        if (!provider || !phone) {
            alert("must select phone service provider and enter phone number");
            return;
        }
        var provider_map = {
            'ATT': 'mms.att.net',
            'TMOBILE': 'tmomail.net',
            'VERIZON': 'vtext.com',
            'SPRINT': 'page.nextel.com'
        };
        var phone_string = phone.replace(/\D/g,'');
        phone_string = phone_string + '@' + provider_map[provider];
        $.post("/add_alert/", {
            phone: phone_string,
            fblink: fblink
        },function(data) {
            location.reload();
        });
    });
});