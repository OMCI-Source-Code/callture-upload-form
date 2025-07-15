
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


function formatDate(formDate, formTime) {
    const date = new Date(formDate);

    const hr = parseInt(formTime.slice(0, 2), 10)
    const min = parseInt(formTime.slice(3), 10)
    date.setHours(hr, min)

    const dtf = new Intl.DateTimeFormat('en', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
    });
    // interesting const name choice :)
    const [{ value: month }, , { value: day }, , { value: year }, , { value: hour }, , { value: minute }, , { value: dayPeriod }] = dtf.formatToParts(date);

    return day + ' ' + month + ' ' + year;
}

// Form submission handler
document
    .getElementById("dataForm")
    .addEventListener("submit", async function (e) {
        e.preventDefault();
        const formData = new FormData(this);

        const fromDate = formData.get("fromDate");
        const fromTime = formData.get("fromTime");
        const toDate = formData.get("toDate");
        const toTime = formData.get("toTime");
        const selectedNumbers = [];

        const dateRange = formatDate(fromDate, fromTime) + ' - ' + formatDate(toDate, toTime);
        console.log(dateRange)
        // Get all checked contacts
        const checkboxes = document.querySelectorAll(
            'input[name="contacts"]:checked'
        );
        checkboxes.forEach((cb) => selectedNumbers.push(cb.value));

        const reqBody = {
            dateRange: dateRange,
            lineNo: selectedNumbers,
        }

        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: JSON.stringify(reqBody), // string or object
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (response.status != 200) {
            console.log(response)
            alert(`Error ${response.status}!\n${response.statusText}`);
        } else {
            alert(`Successfully uploaded to drive!`);
        }

    });