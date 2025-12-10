// liff.js
const LIFF_ID = "2008660278-Ap3kLvYJ";

window.onload = async function () {
    try {
        await liff.init({ liffId: LIFF_ID });

        if (!liff.isLoggedIn()) {
            liff.login();
            return;
        }

        // プロフィール取得
        const profile = await liff.getProfile();

        // LINEユーザーIDを hidden にセット
        document.getElementById("line_user_id").value = profile.userId;

        // 表示名や電話番号を自動入力（必要なら）
        document.getElementById("customer_name").value = profile.displayName;

        // 電話番号は LINE では取れないので空
    } catch (err) {
        console.error("LIFF init error:", err);
    }
};
