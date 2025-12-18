document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("reservation-form");
    if (!form) return;

    const menuSelect = document.getElementById("menu");
    const durationSelect = document.getElementById("duration");
    const dateInput = document.getElementById("date");
    const timeSelect = document.getElementById("time");

    const initialDuration = Number(form.dataset.initialDuration || 60);
    const initialTime = form.dataset.initialTime || null;
    const excludeId = form.dataset.reservationId || null;

    // -----------------------------
    // メニュー → duration 切替
    // -----------------------------
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

    // -----------------------------
    // time-slot API 呼び出し
    // -----------------------------
    async function fetchTimeSlots() {
        if (!dateInput.value || !durationSelect.value) return;

        const params = new URLSearchParams({
            date: dateInput.value,
            duration: durationSelect.value
        });

        if (excludeId) {
            params.append("exclude_id", excludeId);
        }

        const res = await fetch(`/api/time-slots?${params}`);
        const data = await res.json();

        timeSelect.innerHTML = "";

        data.time_slots.forEach(t => {
            const opt = new Option(t, t);

            const isDisabled = data.disabled.includes(t);
            if (isDisabled) {
                opt.disabled = true;
            }

            // ★ 修正ポイント
            if (t === initialTime && !isDisabled) {
                opt.selected = true;
            }

            timeSelect.add(opt);
        });
    }


    // -----------------------------
    // 初期化（← 編集画面で一番重要）
    // -----------------------------
    if (menuSelect) {
        updateDurations(menuSelect.value);
    }

    fetchTimeSlots(); // ← これが無かった

    // -----------------------------
    // イベント
    // -----------------------------
    menuSelect?.addEventListener("change", () => {
        updateDurations(menuSelect.value);
        fetchTimeSlots();
    });

    durationSelect?.addEventListener("change", fetchTimeSlots);
    dateInput?.addEventListener("change", fetchTimeSlots);
});
