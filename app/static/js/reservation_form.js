document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("reservation-form");
    if (!form) return;

    const menuSelect = document.getElementById("menu");
    const durationSelect = document.getElementById("duration");
    const dateInput = document.getElementById("date");
    const timeSelect = document.getElementById("time");

    // 編集画面用初期値（新規予約画面では未定義）
    const initialMenu = form.dataset.initialMenu || null;
    const initialDuration = Number(form.dataset.initialDuration || 60);
    const initialTime = form.dataset.initialTime || null;

    /* ------------------------------
       所要時間切り替え
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

        // 編集画面：既存 duration を再選択
        [...durationSelect.options].forEach(opt => {
            if (Number(opt.value) === initialDuration) {
                opt.selected = true;
            }
        });
    }

    /* ------------------------------
       time-slot API 呼び出し
    ------------------------------ */
    async function loadTimeSlots() {
        if (!dateInput || !durationSelect || !timeSelect) return;

        const date = dateInput.value;
        const duration = durationSelect.value;

        if (!date || !duration) return;

        const res = await fetch(
            `/api/time-slots?date=${date}&duration=${duration}`
        );
        const data = await res.json();

        timeSelect.innerHTML = "";

        data.time_slots.forEach(ts => {
            const opt = document.createElement("option");
            opt.value = ts;
            opt.textContent = ts;

            if (data.disabled && data.disabled.includes(ts)) {
                opt.disabled = true;
            }

            timeSelect.appendChild(opt);
        });

        // 編集画面：既存開始時間を復元
        if (initialTime) {
            [...timeSelect.options].forEach(opt => {
                if (opt.value === initialTime) {
                    opt.selected = true;
                }
            });
        }
    }

    /* ------------------------------
       初期化処理
    ------------------------------ */
    if (menuSelect) {
        if (initialMenu) {
            menuSelect.value = initialMenu;
        }

        updateDurations(menuSelect.value);

        menuSelect.addEventListener("change", () => {
            updateDurations(menuSelect.value);
            loadTimeSlots();
        });
    }

    if (durationSelect) {
        durationSelect.addEventListener("change", loadTimeSlots);
    }

    if (dateInput) {
        dateInput.addEventListener("change", loadTimeSlots);
    }

    // 編集画面：初回ロード時に time-slot を取得
    if (initialTime) {
        loadTimeSlots();
    }
});
