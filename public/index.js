
// Select/Deselect all functionality
document
    .getElementById("selectAll")
    .addEventListener("click", function () {
        const checkboxes = document.querySelectorAll(
            'input[name="contacts"]'
        );
        checkboxes.forEach((cb) => (cb.checked = true));
    });

document
    .getElementById("deselectAll")
    .addEventListener("click", function () {
        const checkboxes = document.querySelectorAll(
            'input[name="contacts"]'
        );
        checkboxes.forEach((cb) => (cb.checked = false));
    });

// Form submission handler
document
    .getElementById("dataForm")
    .addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const selectedContacts = [];

        // Get all checked contacts
        const checkboxes = document.querySelectorAll(
            'input[name="contacts"]:checked'
        );
        checkboxes.forEach((cb) => selectedContacts.push(cb.value));

        console.log("Form Data:", {
            fromDate: formData.get("fromDate"),
            toDate: formData.get("toDate"),
            selectedContacts: selectedContacts,
        });

        alert("Form submitted! Check console for data.");
    });