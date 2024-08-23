// Function to Implement Dropdown Menu
const dropdownButton = document.getElementById('dropdownButton');
const dropdownMenu = document.getElementById('dropdownMenu');
const dropdownIcon = document.getElementById('dropdownIcon');

dropdownButton.addEventListener('click', function() {
    dropdownMenu.classList.toggle('hidden');
    dropdownMenu.classList.toggle('opacity-0');
    dropdownMenu.classList.toggle('-translate-y-40');
    dropdownIcon.classList.toggle('rotate-180');
});

window.addEventListener('click', function(event) {
    if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.classList.add('hidden');
        dropdownMenu.classList.add('opacity-0');
        dropdownMenu.classList.add('-translate-y-40');
        dropdownIcon.classList.remove('rotate-180');
    }
});

// Get the elements for the popover
const infoIcon = document.getElementById('infoIcon');
const popover = document.getElementById('popover');

// Function to show the popover
function showPopover() {
    popover.classList.remove('opacity-0', 'pointer-events-none');
    popover.classList.add('opacity-100', 'pointer-events-auto');
}

// Function to hide the popover
function hidePopover() {
    popover.classList.remove('opacity-100', 'pointer-events-auto');
    popover.classList.add('opacity-0', 'pointer-events-none');
}

// Show the popover on hover over the icon
infoIcon.addEventListener('mouseenter', showPopover);

// Keep the popover visible when hovering over it
popover.addEventListener('mouseenter', showPopover);

// Hide the popover when the mouse leaves both the icon and the popover
infoIcon.addEventListener('mouseleave', function() {
    setTimeout(function() {
        if (!popover.matches(':hover')) {
            hidePopover();
        }
    }, 100);
});
popover.addEventListener('mouseleave', hidePopover);

// Modal-based badge number verification
const newDocketBtn = document.getElementById('newDocketBtn');
const searchDatabaseBtn = document.getElementById('searchDatabaseBtn');
const casesProgressBtn = document.getElementById('casesProgressBtn');
const commandMessagingBtn = document.getElementById('commandMessagingBtn');
const verifyButton = document.getElementById('verifyButton');
const cancelButton = document.getElementById('cancelButton');
const badgeModal = document.getElementById('badgeModal');
const badgeInput = document.getElementById('badgeInput');
let redirectUrl = '';

// Show modal and store redirect URL
function showModal(url) {
    redirectUrl = url;
    badgeModal.classList.remove('hidden');
}

// Hide modal
function hideModal() {
    badgeModal.classList.add('hidden');
}

// Event listeners for buttons to show modal
newDocketBtn.addEventListener('click', function() {
    showModal('{% url "docketforms" %}');
});
searchDatabaseBtn.addEventListener('click', function() {
    showModal('{% url "searchdatabase" %}');
});
casesProgressBtn.addEventListener('click', function() {
    showModal('{% url "casesProgress" %}');
});
commandMessagingBtn.addEventListener('click', function() {
    showModal('{% url "commandmessaging" %}');
});

// Event listener for verify button in modal
verifyButton.addEventListener('click', function() {
    verifyBadgeNumber();
});

// Event listener for cancel button in modal
cancelButton.addEventListener('click', hideModal);




// Function to verify badge number and redirect if correct
function verifyBadgeNumber() {
    const enteredBadge = badgeInput.value;

    // Send AJAX request to backend to verify the badge number
    fetch('{% url "verify_badge" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: new URLSearchParams({
            'officer_staff_ID': enteredBadge
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            hideModal();
            window.location.href = redirectUrl;
        } else {
            alert(data.message || 'Incorrect badge number. Please try again.');
        }
    })
    .catch(error => console.error('Error:', error));
}