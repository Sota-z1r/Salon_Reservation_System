document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("reservation-form");
    if (!form) return;

    const menuSelect = document.getElementById("menu");
    const durationSelect = document.getElementById("duration");
    const dateInput = document.getElementById("date");
    const timeSelect = document.getElementById("time");

    const initialMenu = form.dataset.initialMenu || null;
    const initialDuration = Number(form.dataset.initialDuration || 60);
    const initialTime = form.dataset.initialTime || null;
    const excludeId = form.dataset.reservationId || null;

    /* ------------------------------
       duration 切替
    ------------------------------ */
    function updateDurations(menu) {
        durationSelect.innerHTML = "";

        if (menu === "training") {
            durationSelect.add(new Option("60分", "60"));
        }

        if (menu === "massage") {
            durationSelect.add(new Option("60分", "60"));
            durationSelect.add(new Option("90分", "90"));
            durationSelect.add(new Option("120分", "120"));
        }

        [...durationSelect.options].forEach(opt => {
            if (Number(opt.value) === initialDuration) {
                opt.selected = true;
            }
        });
    }

    /* ------------------------------
       time-slot API
    ------------------------------ */
    async function loadTimeSlots() {
        const date = dateInput.value;
        const duration = durationSelect.value;

        if (!date || !duration) return;

        let url = `/api/time-slots?date=${date}&duration=${duration}`;
        if (excludeId) {
            url += `&exclude_id=${excludeId}`;
        }

        const res = await fetch(url);
        const data = await res.json();

        timeSelect.innerHTML = "";

        data.time_slots.forEach(ts => {
            const opt = document.createElement("option");
            opt.value = ts;
            opt.textContent = ts;

            if (data.disabled.includes(ts)) {
                opt.disabled = true;
            }

            timeSelect.appendChild(opt);
        });

        // 編集画面：既存時間を強制復元
        if (initialTime) {
            const opt = [...timeSelect.options].find(o => o.value === initialTime);
            if (opt) {
                opt.disabled = false;
                opt.selected = true;
            }
        }
    }

    /* ------------------------------
       初期化
    ------------------------------ */
    if (menuSelect && initialMenu) {
        menuSelect.value = initialMenu;
    }

    updateDurations(menuSelect.value);
    loadTimeSlots();

    menuSelect.addEventListener("change", () => {
        updateDurations(menuSelect.value);
        loadTimeSlots();
    });

    durationSelect.addEventListener("change", loadTimeSlots);
    dateInput.addEventListener("change", loadTimeSlots);
});
