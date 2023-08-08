// Toggle Show Password
$(document).ready(function() {
    $('#togglePassword').click(function() {
        var passwordInput = $('#password');

        // Remember the color before changing the class
        var color = $(this).find('.fa').css('color');

        if (passwordInput.attr('type') === 'password') {
            passwordInput.attr('type', 'text');
            $(this).find('.fa').removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            passwordInput.attr('type', 'password');
            $(this).find('.fa').removeClass('fa-eye-slash').addClass('fa-eye');
        }

        // Reapply the color after changing the class
        $(this).find('.fa').css('color', color);
    });

    const $passwordInput = $('#password');
    const $eyeButton = $('#togglePassword');

    $passwordInput.on('focus', function() {
        $eyeButton.find('.fa').css('color', '#0000ff');  // Color when the user is typing
    });

    $passwordInput.on('blur', function() {
        $eyeButton.find('.fa').css('color', '#ffffff');  // Color when the user is no longer typing
    });
});
