
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
        const modal_popup = document.getElementById("modal_popup");
        const submit_btn = document.getElementById("submit-btn");
        submit_btn.classList.add('hide');
        const formData = new FormData(this);

        const fromDateStr = formData.get("fromDate");
        const [fromYear,fromMonth,fromDay] = fromDateStr.split("-").map(Number);
        const fromDate = new Date(fromYear,fromMonth-1,fromDay)
        // const fromTime = formData.get("fromTime");
        const fromTime = "00:00"
        const toDateStr = formData.get("toDate");
        const [toYear,toMonth,toDay] = toDateStr.split("-").map(Number);
        const toDate = new Date(toYear,toMonth-1,toDay)
        const toTime = "23:59"
        // const toTime = formData.get("toTime");
        const selectedNumbers = [];

        const dateRange = formatDate(fromDate, fromTime) + ' - ' + formatDate(toDate, toTime);
        // Get all checked contacts
        const checkboxes = document.querySelectorAll(
            'input[name="contacts"]:checked'
        );
        checkboxes.forEach((cb) => selectedNumbers.push(cb.value));

        const reqBody = {
            dateRange: dateRange,
            lineNo: selectedNumbers,
        }
        modal_popup.textContent = "Uploading...";
        modal_popup.classList.add('show');

        try {
            document.getElementById("loader").style.display = "flex";

            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: JSON.stringify(reqBody), // string or object
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const data = await response.json()
                console.log(response);
                modal_popup.textContent = "Upload failed!"
                setTimeout(() => { modal_popup.classList.remove('show'); }, "1500");
                setTimeout(() => { modal_popup.textContent = `Error ${response.status}: ${data.error}`; modal_popup.classList.add('show'); }, "2000");
                setTimeout(() => { modal_popup.classList.remove('show'); }, "10000");
                throw new Error(`${response.status}: ${data.message}`)
            }

            modal_popup.classList.remove('show');
            setTimeout(() => { modal_popup.textContent = "Upload completed successfully!"; modal_popup.classList.add('show'); }, "500");
            setTimeout(() => { modal_popup.classList.remove('show'); }, "7000");
        } catch (exception) {
            console.error(exception);
            setTimeout(() => {
                if (confirm(`Error: Would you like to try again?`)) {
                    var restart_pending = true;
                    modal_popup.classList.remove('show');
                    if(restart_pending){document.getElementById("submit-btn").click(); restart_pending = false;}
                };
            }, "2350");
            modal_popup.classList.remove('show');
          
        } finally {
            document.getElementById("loader").style.display = "none";
        }
		

    });