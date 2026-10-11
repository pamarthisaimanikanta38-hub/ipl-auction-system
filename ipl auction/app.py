
import time
import requests
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="IPL Auction Arena",
    page_icon="🏏",
    layout="wide"
)

# ---------------- CONFIGURATION ----------------
PURSE = 100.0
BID_INCREMENT = 0.5
TIMER_SECONDS = 15

TEAMS = {
    "SRH": {"name": "Sunrisers Hyderabad", "color": "#ff6500"},
    "CSK": {"name": "Chennai Super Kings", "color": "#ffdc45"},
    "MI":  {"name": "Mumbai Indians", "color": "#36a2ff"},
    "RCB": {"name": "Royal Challengers Bengaluru", "color": "#ff4267"},
}

PLAYERS = [
    ("Virat Kohli", "Batter", "India", 2.0),
    ("MS Dhoni", "Wicketkeeper", "India", 2.0),
    ("Rohit Sharma", "Batter", "India", 2.0),
    ("Jasprit Bumrah", "Bowler", "India", 1.8),
    ("Hardik Pandya", "All-rounder", "India", 1.8),
    ("Ravindra Jadeja", "All-rounder", "India", 1.7),
    ("Suryakumar Yadav", "Batter", "India", 1.7),
    ("KL Rahul", "Wicketkeeper", "India", 1.7),
    ("Yashasvi Jaiswal", "Batter", "India", 1.5),
    ("Shubman Gill", "Batter", "India", 1.6),
    ("Rinku Singh", "Batter", "India", 1.4),
    ("Tilak Varma", "Batter", "India", 1.4),
    ("Ruturaj Gaikwad", "Batter", "India", 1.4),
    ("Ishan Kishan", "Wicketkeeper", "India", 1.4),
    ("Abhishek Sharma", "All-rounder", "India", 1.4),
    ("Sai Sudharsan", "Batter", "India", 1.3),
    ("Arshdeep Singh", "Bowler", "India", 1.3),
    ("Umran Malik", "Bowler", "India", 1.3),
    ("Nitish Kumar Reddy", "All-rounder", "India", 1.2),
    ("Prithvi Shaw", "Batter", "India", 1.2),
    ("Travis Head", "Batter", "Australia", 1.6),
    ("Heinrich Klaasen", "Wicketkeeper", "South Africa", 1.8),
    ("Pat Cummins", "Bowler", "Australia", 1.8),
    ("Bhuvneshwar Kumar", "Bowler", "India", 1.5),
    ("Mohammed Shami", "Bowler", "India", 1.6),
    ("Faf du Plessis", "Batter", "South Africa", 1.5),
    ("Glenn Maxwell", "All-rounder", "Australia", 1.5),
    ("Rashid Khan", "Bowler", "Afghanistan", 1.8),
]

# ---------------- PREMIUM ORANGE/BLACK CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Inter:wght@400;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #522009 0%, transparent 36%),
        radial-gradient(ellipse at 95% 25%, #321307 0%, transparent 30%),
        linear-gradient(145deg, #050505, #160b06, #080808);
    color: #fff7f0;
    font-family: Inter, sans-serif;
}
.block-container {max-width: 1500px; padding-top: 1rem;}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #211006, #080808);
}
[data-testid="stMetric"] {
    background: #17110e;
    border: 1px solid #583019;
    border-radius: 15px;
    padding: 12px;
}
[data-testid="stMetricValue"] {
    color: #ff9a42;
    font-family: 'Barlow Condensed';
}
.stButton > button {
    background: linear-gradient(120deg, #ffb15c, #ff5900);
    color: #160800;
    border: 1px solid #ffb36d;
    border-radius: 11px;
    font-weight: 900;
    min-height: 42px;
    transition: .15s;
}
.stButton > button:hover {
    box-shadow: 0 0 20px #ff650055;
    transform: translateY(-2px);
    border-color: #fff0d6;
}
.hero {
    border: 1px solid #63351c;
    border-radius: 22px;
    padding: 24px;
    background: linear-gradient(110deg, #201108, #100d0b);
    box-shadow: 0 15px 45px #0008;
    margin-bottom: 20px;
}
.hero h1 {
    font-family: 'Barlow Condensed';
    font-size: clamp(42px, 6vw, 72px);
    font-weight: 900;
    line-height: .95;
    margin: 10px 0;
}
.orange {color: #ff7626;}
.muted {
    color: #b5a394;
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 800;
}
.tile {
    border-radius: 15px;
    padding: 13px;
    border: 1px solid var(--team);
    background: linear-gradient(145deg, #24150e, #100d0b);
    min-height: 115px;
}
.tile strong {
    font-family: 'Barlow Condensed';
    font-size: 26px;
    color: var(--team);
}
.tile small {color: #cbbdaf;}
.playerpanel {
    border: 1px solid #58351f;
    background: linear-gradient(145deg, #1c130e, #0b0a09);
    padding: 17px;
    border-radius: 18px;
}
.price {
    font-family: 'Barlow Condensed';
    font-size: clamp(42px, 5vw, 64px);
    font-weight: 900;
    color: #ff9b42;
}
.tag {
    display: inline-block;
    padding: 5px 10px;
    border: 1px solid #75401f;
    border-radius: 30px;
    color: #ffb36d;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1px;
}
.result {
    font-family: 'Barlow Condensed';
    font-size: 40px;
    font-weight: 900;
    text-align: center;
    padding: 14px;
    border-radius: 12px;
    margin: 12px 0;
    animation: pop .3s ease-out;
}
.sold {background: #39e58c; color: #07150c;}
.unsold {background: #e84467; color: white;}
@keyframes pop {
    from {transform: scale(.94); opacity: .4;}
    to {transform: scale(1); opacity: 1;}
}
[data-testid="stImage"] img {
    width: 105px !important;
    height: 135px !important;
    object-fit: cover !important;
    object-position: center !important;
    border-radius: 10px;
    border: 1px solid #70401f;
}
hr {border-color: #392416;}
</style>

<div class="hero">
  <div class="muted">AI & DATA SCIENCE · LIVE AUCTION SIMULATOR</div>
  <h1>AUCTION<span class="orange">//ARENA</span></h1>
  <div class="muted">SMART BIDDING · BUILD YOUR SQUAD · WIN THE GAME</div>
</div>
""", unsafe_allow_html=True)

# ---------------- TEAM LOGOS ----------------
# Minimal transparent monograms, not official franchise logos.
def team_logo(code, size=36):
    color = TEAMS[code]["color"]
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="{size}" height="{size}" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="44"
        fill="none" stroke="{color}" stroke-width="7"/>
      <circle cx="50" cy="50" r="34"
        fill="none" stroke="#ffffff" stroke-opacity=".5"
        stroke-width="2"/>
      <text x="50" y="59" text-anchor="middle"
        font-family="Arial" font-size="25" font-weight="900"
        fill="{color}">{code}</text>
    </svg>
    """

def show_logo(code, size=36):
    st.markdown(team_logo(code, size), unsafe_allow_html=True)

# ---------------- PLAYER PHOTO LOOKUP ----------------
@st.cache_data(ttl=86400, show_spinner=False)
def player_photo(name):
    headers = {"User-Agent": "StudentAuctionArena/1.0"}
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "prop": "pageimages",
                "piprop": "thumbnail",
                "pithumbsize": 350,
                "titles": name,
            },
            headers=headers,
            timeout=3,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            url = page.get("thumbnail", {}).get("source")
            if url:
                return url
    except Exception:
        pass
    return None

# ---------------- STATE ----------------
def initialize():
    defaults = {
        "idx": 0,
        "started": False,
        "status": "READY",
        "price": None,
        "leader": None,
        "deadline": None,
        "teams": {
            code: {"purse": PURSE, "spent": 0.0, "players": []}
            for code in TEAMS
        },
        "history": [],
        "settled": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def current_player():
    if 0 <= st.session_state.idx < len(PLAYERS):
        return PLAYERS[st.session_state.idx]
    return None

def money(amount):
    return f"₹{float(amount):.2f} Cr"

def log_event(event, player, team="—", amount=0):
    st.session_state.history.append({
        "Time": time.strftime("%H:%M:%S"),
        "Event": event,
        "Player": player,
        "Team": team,
        "Bid (Cr)": round(float(amount), 2),
    })

def prepare_lot():
    player = current_player()
    if player:
        st.session_state.price = player[3]
        st.session_state.leader = None
        st.session_state.deadline = time.time() + TIMER_SECONDS
        st.session_state.status = "LIVE"
    else:
        st.session_state.status = "COMPLETE"
        st.session_state.deadline = None

def settle(force=None):
    """
    force=True  : manual SOLD
    force=False : manual UNSOLD
    force=None  : automatic timer settlement
    """
    player = current_player()

    if (
        not player
        or st.session_state.status != "LIVE"
        or st.session_state.idx in st.session_state.settled
    ):
        return

    leader = st.session_state.leader

    if force is True and not leader:
        st.toast("No bid received. Cannot mark SOLD.", icon="⚠️")
        return

    sold = (leader is not None) if force is None else bool(force)

    if sold and leader:
        team = st.session_state.teams[leader]
        amount = float(st.session_state.price)

        if amount > team["purse"]:
            st.session_state.status = "UNSOLD"
            log_event("UNSOLD", player[0], "—", amount)
            st.session_state.settled.append(st.session_state.idx)
            st.session_state.deadline = None
            st.toast("Insufficient purse. Player marked UNSOLD.", icon="⚠️")
            return

        team["purse"] = round(team["purse"] - amount, 2)
        team["spent"] = round(team["spent"] + amount, 2)
        team["players"].append({
            "Player": player[0],
            "Role": player[1],
            "Price (Cr)": amount,
        })

        st.session_state.status = "SOLD"
        log_event("SOLD", player[0], leader, amount)
        st.toast(f"🔨 SOLD! {player[0]} → {leader}", icon="🏏")

    else:
        st.session_state.status = "UNSOLD"
        log_event("UNSOLD", player[0], "—", st.session_state.price or 0)
        st.toast(f"UNSOLD: {player[0]}", icon="🔔")

    st.session_state.settled.append(st.session_state.idx)
    st.session_state.deadline = None

def next_player():
    st.session_state.idx += 1
    prepare_lot()

initialize()

# ---------------- AUTO TIMER ----------------
if (
    st.session_state.started
    and st.session_state.status == "LIVE"
    and st.session_state.deadline is not None
):
    remaining_now = st.session_state.deadline - time.time()

    if remaining_now <= 0:
        # Highest bidder wins; no bids means UNSOLD.
        settle()
        st.rerun()
    else:
        st_autorefresh(
            interval=1000,
            key=f"timer_{st.session_state.idx}_{int(st.session_state.deadline)}",
        )

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🏏 AUCTION CONTROL")
    page = st.radio(
        "Navigate",
        ["Live Auction", "Teams & Squads", "Player Explorer", "Analytics"],
    )

    st.divider()
    st.markdown("### FRANCHISE PURSES")

    for code, meta in TEAMS.items():
        team = st.session_state.teams[code]
        show_logo(code, 30)
        st.caption(f"{code} · {money(team['purse'])} remaining")
        st.progress(max(0.0, min(1.0, team["purse"] / PURSE)))

    if st.button("♻ RESET AUCTION", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ---------------- LIVE AUCTION ----------------
if page == "Live Auction":
    sold_count = sum(
        len(team["players"])
        for team in st.session_state.teams.values()
    )
    unsold_count = sum(
        event["Event"] == "UNSOLD"
        for event in st.session_state.history
    )
    bid_count = sum(
        event["Event"] == "BID"
        for event in st.session_state.history
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("PLAYER POOL", len(PLAYERS))
    m2.metric("SOLD", sold_count)
    m3.metric("UNSOLD", unsold_count)
    m4.metric("TOTAL BIDS", bid_count)

    st.markdown("## 🏟️ FRANCHISE WAR ROOM")
    cols = st.columns(4)

    for col, (code, meta) in zip(cols, TEAMS.items()):
        team = st.session_state.teams[code]
        with col:
            show_logo(code, 42)
            st.markdown(
                f"""<div class="tile" style="--team:{meta['color']}">
                <strong>{code}</strong>
                <h3>{money(team['purse'])}</h3>
                <small>{meta['name']}<br>
                {len(team['players'])} players · {money(team['spent'])} spent
                </small></div>""",
                unsafe_allow_html=True,
            )

    st.markdown("## 🎯 LIVE PLAYER LOT")
    player = current_player()

    if player is None or st.session_state.status == "COMPLETE":
        st.success("🏆 AUCTION COMPLETE — All players processed.")
        st.balloons()

    else:
        if st.session_state.price is None:
            prepare_lot()

        left, right = st.columns([1, 1.4], gap="large")

        with left:
            st.markdown('<div class="playerpanel">', unsafe_allow_html=True)
            st.markdown(
                f'<span class="tag">LOT {st.session_state.idx + 1:02d}'
                f' / {len(PLAYERS)}</span> '
                f'<span class="tag">{st.session_state.status}</span>',
                unsafe_allow_html=True,
            )

            photo = player_photo(player[0])
            if photo:
                st.image(photo, width=105)
            else:
                initials = "".join(
                    word[0] for word in player[0].split()[:2]
                )
                st.markdown(
                    f"""<div style="width:105px;height:135px;
                    border-radius:10px;background:#24150e;
                    border:1px solid #70401f;display:flex;
                    align-items:center;justify-content:center;
                    font-size:32px;font-weight:900;color:#ff9b42">
                    {initials}</div>""",
                    unsafe_allow_html=True,
                )

            st.markdown(f"### {player[0]}")
            st.caption(f"{player[2]} · {player[1]}")
            st.markdown(f"**Base price:** {money(player[3])}")
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="playerpanel">', unsafe_allow_html=True)
            st.markdown(
                '<span class="muted">CURRENT HIGHEST BID</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="price">{money(st.session_state.price or 0)}</div>',
                unsafe_allow_html=True,
            )

            leader = st.session_state.leader
            if leader:
                show_logo(leader, 38)
                st.markdown(f"**Leading team: {leader}**")
            else:
                st.markdown('<span class="tag">AWAITING FIRST BID</span>',
                            unsafe_allow_html=True)

            remaining = (
                max(0, int(st.session_state.deadline - time.time() + 0.999))
                if st.session_state.deadline else 0
            )
            st.markdown(
                f'<div class="muted">TIME REMAINING</div>'
                f'<div class="price">{remaining:02d} SEC</div>',
                unsafe_allow_html=True,
            )
            st.progress(remaining / TIMER_SECONDS)

            st.markdown("### PLACE YOUR BID")
            bid_cols = st.columns(2)

            for col, (code, meta) in zip(bid_cols * 2, TEAMS.items()):
                with col:
                    show_logo(code, 32)

                    leading = leader == code
                    if leading:
                        label = f"LEADING · {code}"
                    elif leader is None:
                        label = f"OPEN BID · {code}"
                    else:
                        label = f"BID · {code} +{BID_INCREMENT:.2f}"

                    disabled = (
                        not st.session_state.started
                        or st.session_state.status != "LIVE"
                        or leading
                    )

                    if st.button(
                        label,
                        key=f"bid_{code}_{st.session_state.idx}",
                        disabled=disabled,
                        use_container_width=True,
                    ):
                        amount = float(st.session_state.price)
                        if leader:
                            amount += BID_INCREMENT

                        team = st.session_state.teams[code]
                        if amount > team["purse"]:
                            st.warning(f"{code}: insufficient purse.")
                        else:
                            st.session_state.price = amount
                            st.session_state.leader = code
                            st.session_state.deadline = time.time() + TIMER_SECONDS
                            log_event("BID", player[0], code, amount)
                            st.toast(f"{code} bids {money(amount)}", icon="🔔")
                            st.rerun()

            sold_col, unsold_col = st.columns(2)

            with sold_col:
                if st.button(
                    "🔨 SOLD!",
                    key=f"sold_{st.session_state.idx}",
                    disabled=(
                        not st.session_state.started
                        or st.session_state.status != "LIVE"
                        or not leader
                    ),
                    use_container_width=True,
                ):
                    settle(True)
                    st.rerun()

            with unsold_col:
                if st.button(
                    "✕ UNSOLD",
                    key=f"unsold_{st.session_state.idx}",
                    disabled=(
                        not st.session_state.started
                        or st.session_state.status != "LIVE"
                    ),
                    use_container_width=True,
                ):
                    settle(False)
                    st.rerun()

            if st.session_state.status == "SOLD":
                show_logo(st.session_state.leader, 44)
                st.markdown(
                    f'<div class="result sold">🔨 SOLD!'
                    f'<div style="font-family:Inter;font-size:13px">'
                    f'{player[0]} → {st.session_state.leader} · '
                    f'{money(st.session_state.price)}</div></div>',
                    unsafe_allow_html=True,
                )

            elif st.session_state.status == "UNSOLD":
                st.markdown(
                    f'<div class="result unsold">UNSOLD'
                    f'<div style="font-family:Inter;font-size:13px">'
                    f'{player[0]} · No winning bid</div></div>',
                    unsafe_allow_html=True,
                )

            if st.session_state.status in ("SOLD", "UNSOLD"):
                if st.button(
                    "NEXT PLAYER →",
                    key=f"next_{st.session_state.idx}",
                    use_container_width=True,
                ):
                    next_player()
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        if not st.session_state.started:
            if st.button("🚨 START AUCTION", use_container_width=True):
                st.session_state.started = True
                prepare_lot()
                st.toast("Auction started!", icon="🏏")
                st.rerun()

    st.markdown("## 📡 LIVE AUCTION FEED")
    if st.session_state.history:
        st.dataframe(
            pd.DataFrame(st.session_state.history[::-1]).head(15),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("Auction activity will appear here.")

# ---------------- SQUADS ----------------
elif page == "Teams & Squads":
    st.markdown("## 🧢 TEAMS & FINAL SQUADS")

    for code, meta in TEAMS.items():
        team = st.session_state.teams[code]
        with st.expander(
            f"{code} · {meta['name']} · {len(team['players'])} players",
            expanded=True,
        ):
            show_logo(code, 42)
            st.write(f"**Purse remaining:** {money(team['purse'])}")
            if team["players"]:
                st.dataframe(
                    pd.DataFrame(team["players"]),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.caption("No players purchased yet.")

# ---------------- PLAYER EXPLORER ----------------
elif page == "Player Explorer":
    st.markdown("## 🔎 PLAYER EXPLORER")
    df = pd.DataFrame(
        PLAYERS,
        columns=["Player", "Role", "Country", "Base Price (Cr)"],
    )
    search = st.text_input("Search player")
    role = st.selectbox(
        "Role",
        ["All"] + sorted(df["Role"].unique().tolist()),
    )

    if search:
        df = df[df["Player"].str.contains(search, case=False, na=False)]
    if role != "All":
        df = df[df["Role"] == role]

    st.dataframe(df, hide_index=True, use_container_width=True)

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.markdown("## 📊 AUCTION ANALYTICS")
    rows = []

    for code, team in st.session_state.teams.items():
        rows.append({
            "Team": code,
            "Players": len(team["players"]),
            "Spent (Cr)": round(team["spent"], 2),
            "Purse remaining (Cr)": round(team["purse"], 2),
        })

    df = pd.DataFrame(rows)
    left, right = st.columns(2)

    with left:
        st.markdown("### Team spending")
        st.bar_chart(df.set_index("Team")["Spent (Cr)"])

    with right:
        st.markdown("### Remaining purse")
        st.bar_chart(df.set_index("Team")["Purse remaining (Cr)"])

    st.dataframe(df, hide_index=True, use_container_width=True)

    if st.session_state.history:
        st.download_button(
            "EXPORT AUCTION HISTORY CSV",
            pd.DataFrame(st.session_state.history).to_csv(index=False),
            "auction_history.csv",
            "text/csv",
        )

st.markdown(
    "<hr><div style='text-align:center;color:#a17c61;"
    "font-size:10px;letter-spacing:2px'>"
    "AUCTION//ARENA · EDUCATIONAL SIMULATOR · "
    "NOT AN OFFICIAL IPL PRODUCT</div>",
    unsafe_allow_html=True,
)