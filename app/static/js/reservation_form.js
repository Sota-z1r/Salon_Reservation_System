document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("reservation-form");
    if (!form) return;

    const menuSelect = document.getElementById("menu");
    const durationSelect = document.getElementById("duration");
    const timeSelect = document.getElementById("time");

    // 編集画面用データ（新規予約画面では未定義）
    const currentMenu = form.dataset.initialMenu || null;
    const currentDuration = Number(form.dataset.initialDuration || 60);
    const currentTime = form.dataset.initialTime || null;

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
            if (Number(opt.value) === currentDuration) {
                opt.selected = true;
            }
        });
    }

    // メニュー初期化
    if (menuSelect) {
        if (currentMenu) {
            menuSelect.value = currentMenu;
        }

        updateDurations(menuSelect.value);

        menuSelect.addEventListener("change", () => {
            updateDurations(menuSelect.value);
        });
    }

    // 編集画面：開始時間の再選択
    if (timeSelect && currentTime) {
        [...timeSelect.options].forEach(opt => {
            if (opt.value === currentTime) {
                opt.selected = true;
            }
        });
    }
});
