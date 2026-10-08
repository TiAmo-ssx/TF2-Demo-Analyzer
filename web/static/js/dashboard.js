// 依赖 dashboard.html 里注入的全局变量：
//   players    —— 玩家图表数据
//   teamChart  —— 队伍图表数据
//   I18N       —— 当前语言的翻译字典


const I18N = window.I18N || {};

function tr(key) {
    return I18N[key] || key;
}


// ========================================================
// 基础数据
// ========================================================

const labels = players.map(p => p.name);


// ========================================================
// 通用横向柱状图配置
// ========================================================

function createHorizontalBarChart(canvasId, label, values) {

    new Chart(
        document.getElementById(canvasId),
        {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: label,
                        data: values,
                        borderWidth: 0,
                        borderRadius: 5,
                        barPercentage: 0.72,
                        categoryPercentage: 0.8
                    }
                ]
            },

            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                animation: false,

                plugins: {
                    legend: {
                        display: false
                    },

                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return (
                                    " " +
                                    label +
                                    ": " +
                                    context.raw
                                );
                            }
                        }
                    }
                },

                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    },

                    y: {
                        ticks: {
                            autoSkip: false,
                            font: {
                                size: 11
                            },
                            padding: 6
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        }
    );
}


// ========================================================
// KDA
// ========================================================

new Chart(
    document.getElementById("kdaChart"),
    {
        type: "bar",

        data: {
            labels: labels,

            datasets: [
                {
                    label: "Kills",
                    data: players.map(p => p.kills),
                    borderRadius: 4
                },
                {
                    label: "Deaths",
                    data: players.map(p => p.deaths),
                    borderRadius: 4
                },
                {
                    label: "Assists",
                    data: players.map(p => p.assists),
                    borderRadius: 4
                }
            ]
        },

        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            animation: false,

            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                },

                y: {
                    ticks: {
                        autoSkip: false,
                        font: {
                            size: 11
                        },
                        padding: 6
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    }
);


// ========================================================
// Score
// ========================================================

createHorizontalBarChart(
    "scoreChart",
    "Score",
    players.map(p => p.points)
);


// ========================================================
// Damage
// ========================================================

createHorizontalBarChart(
    "damageChart",
    "Damage",
    players.map(p => p.damage)
);


// ========================================================
// Healing
// ========================================================

createHorizontalBarChart(
    "healingChart",
    "Healing",
    players.map(p => p.healing)
);


// ========================================================
// Objective
// ========================================================

new Chart(
    document.getElementById("objectiveChart"),
    {
        type: "bar",

        data: {
            labels: labels,

            datasets: [
                {
                    label: "Captures",
                    data: players.map(p => p.captures),
                    borderRadius: 4
                },
                {
                    label: "Defenses",
                    data: players.map(p => p.defenses),
                    borderRadius: 4
                }
            ]
        },

        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            animation: false,

            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                },

                y: {
                    ticks: {
                        autoSkip: false,
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    }
);


// ========================================================
// Special
// ========================================================

new Chart(
    document.getElementById("specialChart"),
    {
        type: "bar",

        data: {
            labels: labels,

            datasets: [
                {
                    label: "Headshots",
                    data: players.map(p => p.headshots),
                    borderRadius: 4
                },
                {
                    label: "Backstabs",
                    data: players.map(p => p.backstabs),
                    borderRadius: 4
                },
                {
                    label: "Uber",
                    data: players.map(p => p.ubercharges),
                    borderRadius: 4
                },
                {
                    label: "Buildings",
                    data: players.map(p => p.buildings),
                    borderRadius: 4
                }
            ]
        },

        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            animation: false,

            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                },

                y: {
                    ticks: {
                        autoSkip: false,
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    }
);


// ========================================================
// 玩家信息卡片
// ========================================================

const playerCard =
    document.getElementById("playerCard");

const playerCardHeader =
    document.getElementById("playerCardHeader");

const playerCardClose =
    document.getElementById("playerCardClose");


// ========================================================
// 玩家数据映射
// ========================================================

const playerMap = {};

players.forEach(player => {
    playerMap[player.id] = player;
});


// ========================================================
// 渲染玩家信息卡片
// ========================================================

function renderPlayerCard(player) {

    if (!playerCard || !player) {
        return;
    }


    // -------------------------------------------------
    // 玩家名称
    // -------------------------------------------------

    const nameElement =
        document.getElementById("cardPlayerName");

    if (nameElement) {
        nameElement.textContent =
            player.name || tr('player_unknown');
    }


    // -------------------------------------------------
    // 玩家队伍
    // -------------------------------------------------

    const teamElement =
        document.getElementById("cardPlayerTeam");

    if (teamElement) {

        let teamName = tr('team_other');
        let teamClass = "other";

        if (player.team === "red") {
            teamName = "RED";
            teamClass = "red";
        } else if (player.team === "blue") {
            teamName = "BLU";
            teamClass = "blue";
        }

        teamElement.textContent = teamName;
        teamElement.className =
            "player-card-team " + teamClass;
    }


    // -------------------------------------------------
    // KDA
    // -------------------------------------------------

    const kills =
        document.getElementById("cardKills");

    const deaths =
        document.getElementById("cardDeaths");

    const assists =
        document.getElementById("cardAssists");

    if (kills) {
        kills.textContent = player.kills ?? 0;
    }

    if (deaths) {
        deaths.textContent = player.deaths ?? 0;
    }

    if (assists) {
        assists.textContent = player.assists ?? 0;
    }


    // -------------------------------------------------
    // 其他统计数据
    // -------------------------------------------------

    const stats = {
        cardPoints: player.points,
        cardDamage: player.damage,
        cardHealing: player.healing,
        cardCaptures: player.captures,
        cardDefenses: player.defenses,
        cardHeadshots: player.headshots,
        cardBackstabs: player.backstabs,
        cardUber: player.ubercharges,
        cardBuildings: player.buildings,
        cardTeleports: player.teleports,
        cardDominations: player.dominations,
        cardRevenges: player.revenges
    };

    Object.entries(stats).forEach(([elementId, value]) => {

        const element =
            document.getElementById(elementId);

        if (element) {
            element.textContent = value ?? 0;
        }
    });


    // -------------------------------------------------
    // 使用过的职业
    // -------------------------------------------------

    const classContainer =
        document.getElementById("cardClasses");

    if (classContainer) {

        classContainer.innerHTML = "";

        if (player.classes && player.classes.length > 0) {

            player.classes.forEach(cls => {

                const span =
                    document.createElement("span");

                span.className = "player-class";

                span.textContent =
                    `${cls.name} ×${cls.count}`;

                classContainer.appendChild(span);
            });

        } else {

            classContainer.textContent = tr('no_class_data');
        }
    }


    // -------------------------------------------------
    // 武器数据
    // -------------------------------------------------

    const weaponContainer =
        document.getElementById("cardWeapons");

    if (weaponContainer) {

        weaponContainer.innerHTML = "";

        const weaponList =
            [...(player.weapons || [])]
                .sort((a, b) => (b.kills || 0) - (a.kills || 0))
                .slice(0, 12);

        if (weaponList.length === 0) {

            weaponContainer.textContent = tr('no_weapon_data');

        } else {

            weaponList.forEach(weapon => {

                const row =
                    document.createElement("div");

                row.className = "player-weapon";

                const name =
                    document.createElement("span");

                name.className = "player-weapon-name";

                name.textContent =
                    weapon.name || tr('player_unknown');

                const kills =
                    document.createElement("span");

                kills.className = "player-weapon-kills";

                kills.textContent = weapon.kills || 0;

                row.appendChild(name);
                row.appendChild(kills);

                weaponContainer.appendChild(row);
            });
        }
    }
}


// ========================================================
// 卡片出现位置（只在 Hover 时定位一次）
// ========================================================

function movePlayerCard(event) {

    if (!playerCard) {
        return;
    }

    const cardWidth = playerCard.offsetWidth || 380;
    const cardHeight = playerCard.offsetHeight || 520;

    const padding = 15;

    let x = event.clientX + 18;
    let y = event.clientY + 18;

    // 防止超出右边
    if (x + cardWidth > window.innerWidth - padding) {
        x = event.clientX - cardWidth - 18;
    }

    // 防止超出左边
    if (x < padding) {
        x = padding;
    }

    // 防止超出底部
    if (y + cardHeight > window.innerHeight - padding) {
        y = window.innerHeight - cardHeight - padding;
    }

    // 防止超出顶部
    if (y < padding) {
        y = padding;
    }

    playerCard.style.left = `${x}px`;
    playerCard.style.top = `${y}px`;
}


// ========================================================
// 关闭玩家卡片
// ========================================================

function hidePlayerCard() {

    if (playerCard) {
        playerCard.classList.remove("show");
    }
}


// ========================================================
// × 关闭按钮
// ========================================================

if (playerCardClose) {

    playerCardClose.addEventListener("click", function(event) {

        event.preventDefault();
        event.stopPropagation();

        hidePlayerCard();
    });
}


// ========================================================
// 玩家卡片拖拽
// ========================================================

let isDraggingPlayerCard = false;
let dragOffsetX = 0;
let dragOffsetY = 0;

if (playerCardHeader) {

    playerCardHeader.addEventListener("mousedown", function(event) {

        // 点击关闭按钮时不进行拖拽
        if (event.target.closest(".player-card-close")) {
            return;
        }

        if (!playerCard) {
            return;
        }

        isDraggingPlayerCard = true;

        const rect = playerCard.getBoundingClientRect();

        dragOffsetX = event.clientX - rect.left;
        dragOffsetY = event.clientY - rect.top;

        playerCard.classList.add("dragging");

        event.preventDefault();
    });
}


// ========================================================
// 拖拽移动
// ========================================================

document.addEventListener("mousemove", function(event) {

    if (!isDraggingPlayerCard || !playerCard) {
        return;
    }

    const cardWidth = playerCard.offsetWidth;
    const cardHeight = playerCard.offsetHeight;

    const padding = 10;

    let x = event.clientX - dragOffsetX;
    let y = event.clientY - dragOffsetY;

    x = Math.max(padding, x);
    x = Math.min(x, window.innerWidth - cardWidth - padding);

    y = Math.max(padding, y);
    y = Math.min(y, window.innerHeight - cardHeight - padding);

    playerCard.style.left = `${x}px`;
    playerCard.style.top = `${y}px`;
});


// ========================================================
// 松开鼠标
// ========================================================

document.addEventListener("mouseup", function() {

    if (!isDraggingPlayerCard) {
        return;
    }

    isDraggingPlayerCard = false;

    if (playerCard) {
        playerCard.classList.remove("dragging");
    }
});


// ========================================================
// 玩家名字 Hover
// ========================================================

document.querySelectorAll(".player-name").forEach(element => {

    element.addEventListener("mouseenter", function(event) {

        const id = Number(element.dataset.playerId);
        const player = playerMap[id];

        if (!player) {
            console.warn(tr('player_not_found') + ":", id);
            return;
        }

        // 更新卡片内容
        renderPlayerCard(player);

        // 定位卡片（只在进入玩家名字时执行一次）
        movePlayerCard(event);

        // 显示卡片
        playerCard.classList.add("show");
    });
});
