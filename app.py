from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
import os
from functools import wraps

app = Flask(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fairplay.db"
)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            short_name TEXT NOT NULL,
            gender TEXT NOT NULL CHECK(gender IN ('men', 'women')),
            logo TEXT DEFAULT '',
            matches INTEGER NOT NULL DEFAULT 0,
            fairplay_points INTEGER NOT NULL DEFAULT 0,
            penalty_points INTEGER NOT NULL DEFAULT 0
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM teams"
    ).fetchone()[0]

    # Insert teams only when the database is empty.
    if count == 0:

        mens = [
            ("Chennai Super Kings RA", "CSK",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/CSK.png"),
            ("Mumbai Indians RA", "MI",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/MI.png"),
            ("Royal Challengers Bengaluru RA", "RCB",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/RCB.png"),
            ("Kolkata Knight Riders RA", "KKR",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/KKR.png"),
            ("Gujarat Titans RA", "GT",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/GT.png"),
            ("Lucknow Super Giants RA", "LSG",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/LSG.png"),
            ("Delhi Capitals RA", "DC",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/DC.png"),
            ("Rajasthan Royals RA", "RR",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/RR.png"),
            ("Sunrisers Hyderabad RA", "SRH",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/SRH.png"),
            ("Punjab Kings RA", "PBKS",
             "https://scores.iplt20.com/ipl-mono/img/team-logos-2/PBKS.png"),
        ]

        womens = [
            ("Mumbai Indians Women RA", "MI-W",
             "https://www.wplt20.com/static-assets/images/teams/641.png"),
            ("Delhi Capitals Women RA", "DC-W",
             "https://www.wplt20.com/static-assets/images/teams/640.png"),
            ("Royal Challengers Bengaluru Women RA", "RCB-W",
             "https://www.wplt20.com/static-assets/images/teams/642.png"),
            ("UP Warriorz RA", "UPW",
             "https://www.wplt20.com/static-assets/images/teams/644.png"),
            ("Gujarat Giants RA", "GG",
             "https://www.wplt20.com/static-assets/images/teams/643.png"),
        ]

        for name, short_name, logo in mens:
            conn.execute("""
                INSERT INTO teams
                (name, short_name, gender, logo)
                VALUES (?, ?, 'men', ?)
            """, (name, short_name, logo))

        for name, short_name, logo in womens:
            conn.execute("""
                INSERT INTO teams
                (name, short_name, gender, logo)
                VALUES (?, ?, 'women', ?)
            """, (name, short_name, logo))

    else:
        # IMPORTANT:
        # Your existing fairplay.db may already contain the old names.
        # This updates the existing names WITHOUT deleting matches/points.
        ra_names = {
            "Chennai Super Kings": "Chennai Super Kings RA",
            "Mumbai Indians": "Mumbai Indians RA",
            "Royal Challengers Bengaluru": "Royal Challengers Bengaluru RA",
            "Kolkata Knight Riders": "Kolkata Knight Riders RA",
            "Gujarat Titans": "Gujarat Titans RA",
            "Lucknow Super Giants": "Lucknow Super Giants RA",
            "Delhi Capitals": "Delhi Capitals RA",
            "Rajasthan Royals": "Rajasthan Royals RA",
            "Sunrisers Hyderabad": "Sunrisers Hyderabad RA",
            "Punjab Kings": "Punjab Kings RA",
            "Mumbai Indians Women": "Mumbai Indians Women RA",
            "Delhi Capitals Women": "Delhi Capitals Women RA",
            "Royal Challengers Bengaluru Women": "Royal Challengers Bengaluru Women RA",
            "UP Warriorz": "UP Warriorz RA",
            "Gujarat Giants": "Gujarat Giants RA",
        }

        for old_name, new_name in ra_names.items():
            conn.execute(
                """
                UPDATE teams
                SET name = ?
                WHERE name = ?
                """,
                (new_name, old_name)
            )

        # Safety: if any existing team name does not have RA,
        # append it automatically.
        conn.execute("""
            UPDATE teams
            SET name = name || ' RA'
            WHERE name NOT LIKE '% RA'
        """)

    conn.commit()
    conn.close()


# ============================================================
# AUTHENTICATION
# ============================================================

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped_view


# ============================================================
# PAGE HEAD / NAVBAR
# Styling is kept in static/style.css
# ============================================================

PAGE_HEAD = """<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">
    <title>{{ page_title|default('TPL Fairplay Standings') }}</title>
    <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='style.css') }}\">
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='kore.png') }}">
    
</head>
<body>
"""

PAGE_FOOTER = """
<footer class="site-footer">
    <div class="footer-inner">
        <span class="footer-powered">POWERED BY</span>

        <img src="/static/kore.png"
             alt="TPL Logo"
             class="footer-logo">
    </div>
</footer>
</body>
</html>
"""

NAV_BAR = """
<nav>
    <a href=\"/mens\" class=\"brand\">
        <img
            src=\"{{ url_for('static', filename='tppl.png') }}\"
            alt=\"TPL Logo\"
            class=\"nav-logo\"
            onerror=\"this.style.display='none';\"
        >
        
    </a>

    <div class=\"nav-links\">
        <a href=\"/mens\">MEN'S</a>
        <a href=\"/womens\">WOMEN'S</a>
        
    </div>
</nav>
"""

# ============================================================
# PUBLIC STANDINGS
# ============================================================

STANDINGS_TEMPLATE = PAGE_HEAD + NAV_BAR + """
<div class="page">

    <div class="hero">
        <div class="eyebrow">TPL Fairplay Rankings</div>
        <h1>{{ title }}</h1>
        <p>Season 04</p>
    </div>

    <div class="card">
        {% if teams %}
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Team</th>
                        <th>Matches</th>
                        <th>FP</th>
                        
                        <th>Avg FP</th>
                    </tr>
                </thead>

                <tbody>
                {% for team in teams %}
                    <tr>
                        <td class="rank {% if loop.index <= 3 %}top{% endif %}">
                            #{{ loop.index }}
                        </td>

                        <td>
                            <div class="team">
                                <div class="logo">
                                    {% if team.logo %}
                                        <img
                                            src="{{ team.logo }}"
                                            alt="{{ team.name }}"
                                            onerror="this.style.display='none';"
                                        >
                                    {% else %}
                                        {{ team.short_name }}
                                    {% endif %}
                                </div>

                                <div>
                                    <div class="team-name">
                                        {{ team.name }}
                                    </div>
                                    <div class="team-code">
                                        {{ team.short_name }}
                                    </div>
                                </div>
                            </div>
                        </td>

                        <td>{{ team.matches }}</td>

                        <td class="positive">
                            +{{ team.fairplay_points }}
                        </td>

                       

                        <td class="total">
    {{ "%.3f"|format(team.avg_fp) }}
</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>

        {% else %}
            <div style="padding:50px;text-align:center;color:#667085;">
                No teams found.
            </div>
        {% endif %}
    </div>
</div>
""" + PAGE_FOOTER


def standings_page(gender, title):
    conn = get_db()

    teams = conn.execute("""
        SELECT *,
               CASE
                   WHEN matches > 0
                   THEN CAST(fairplay_points AS REAL) / matches
                   ELSE 0
               END AS avg_fp
        FROM teams
        WHERE gender = ?
        ORDER BY avg_fp DESC,
                 fairplay_points DESC,
                 name ASC
    """, (gender,)).fetchall()

    conn.close()

    return render_template_string(
        STANDINGS_TEMPLATE,
        teams=teams,
        title=title
    )


@app.route("/")
def index():
    return redirect(url_for("mens_standings"))


@app.route("/mens")
def mens_standings():
    return standings_page(
        "men",
        "Men's Fairplay Standings"
    )


@app.route("/womens")
def womens_standings():
    return standings_page(
        "women",
        "Women's Fairplay Standings"
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

LOGIN_TEMPLATE = PAGE_HEAD + NAV_BAR + """
<div class="login-box">
    <div class="card">
        <h1>Admin Login</h1>

        <p style="color:#667085;">
            Sign in to update Fairplay standings.
        </p>

        {% if error %}
            <div
                class="flash"
                style="background:#fef3f2;color:#b42318;"
            >
                {{ error }}
            </div>
        {% endif %}

        <form method="post">

            <div class="login-field">
                <label>Username</label>
                <input
                    name="username"
                    autocomplete="username"
                    required
                >
            </div>

            <div class="login-field">
                <label>Password</label>
                <input
                    name="password"
                    type="password"
                    autocomplete="current-password"
                    required
                >
            </div>

            <button
                class="btn btn-primary login-button"
                type="submit"
            >
                Login
            </button>

        </form>
    </div>
</div>
""" + PAGE_FOOTER


@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if session.get("logged_in"):
        return redirect(url_for("admin_mens"))

    error = None

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):
            session["logged_in"] = True
            return redirect(url_for("admin_mens"))

        error = "Invalid username or password."

    return render_template_string(
        LOGIN_TEMPLATE,
        error=error
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

ADMIN_TEMPLATE = PAGE_HEAD + NAV_BAR + """
<div class="page">

    <div class="hero">
        <div class="eyebrow">Admin Dashboard</div>
        <h1>{{ title }}</h1>
        <p>
            Update matches, fairplay points,
            penalty points and team names.
        </p>
    </div>

    <div class="admin-nav">

        <a
            href="/admin/mens"
            class="{% if gender == 'men' %}active{% endif %}"
        >
            Men's Teams
        </a>

        <a
            href="/admin/womens"
            class="{% if gender == 'women' %}active{% endif %}"
        >
            Women's Teams
        </a>

        <a href="/logout">
            Logout
        </a>
    </div>

    {% with messages = get_flashed_messages() %}
        {% for message in messages %}
            <div class="flash">
                {{ message }}
            </div>
        {% endfor %}
    {% endwith %}

    <div class="card" style="padding:20px;">

        {% for team in teams %}

            <div class="team-admin">

                <div class="team-admin-top">

                    <div>
                        <div class="team-admin-name">
                            {{ team.name }}
                        </div>

                        <div style="
                            color:#98a2b3;
                            font-size:12px;
                            margin-top:3px;
                        ">
                            {{ team.short_name }}
                        </div>
                    </div>

                    <span class="badge">
                        {{ team.gender }}
                    </span>

                </div>

                <form method="post" action="/admin/update">

                    <input
                        type="hidden"
                        name="id"
                        value="{{ team.id }}"
                    >

                    <input
                        type="hidden"
                        name="gender"
                        value="{{ gender }}"
                    >

                    <div class="form-grid">

                        <div class="field">
                            <label>Team Name</label>

                            <input
                                type="text"
                                name="name"
                                value="{{ team.name }}"
                                required
                            >
                        </div>

                        <div class="field">
                            <label>Matches</label>

                            <input
                                type="number"
                                name="matches"
                                min="0"
                                value="{{ team.matches }}"
                                required
                            >
                        </div>

                        <div class="field">
                            <label>Fairplay Points</label>

                            <input
                                type="number"
                                name="fairplay_points"
                                min="0"
                                value="{{ team.fairplay_points }}"
                                required
                            >
                        </div>

                        

                        <div
                            class="field"
                            style="grid-column:1/-1;"
                        >
                            <label>Logo URL</label>

                            <input
                                type="url"
                                name="logo"
                                value="{{ team.logo }}"
                                placeholder="https://..."
                            >
                        </div>

                    </div>

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        margin-top:15px;
                        gap:15px;
                    ">

                        

                        <button
                            class="btn btn-primary"
                            type="submit"
                        >
                            Save Changes
                        </button>

                    </div>

                </form>

            </div>

        {% endfor %}

    </div>
</div>
""" + PAGE_FOOTER


def admin_page(gender, title):

    conn = get_db()

    teams = conn.execute("""
        SELECT *
        FROM teams
        WHERE gender = ?
        ORDER BY name ASC
    """, (gender,)).fetchall()

    conn.close()

    return render_template_string(
        ADMIN_TEMPLATE,
        teams=teams,
        gender=gender,
        title=title
    )


@app.route("/admin/mens")
@login_required
def admin_mens():
    return admin_page(
        "men",
        "Men's Teams"
    )


@app.route("/admin/womens")
@login_required
def admin_womens():
    return admin_page(
        "women",
        "Women's Teams"
    )


# ============================================================
# UPDATE TEAM
# ============================================================

@app.route("/admin/update", methods=["POST"])
@login_required
def update_team():

    gender = request.form.get("gender", "men")

    destination = (
        "admin_mens"
        if gender == "men"
        else "admin_womens"
    )

    try:

        team_id = int(request.form.get("id"))

        name = request.form.get(
            "name",
            ""
        ).strip()

        matches = int(
            request.form.get("matches", 0)
        )

        fairplay_points = int(
            request.form.get("fairplay_points", 0)
        )

        

        logo = request.form.get(
            "logo",
            ""
        ).strip()

        # Always keep RA after the team name.
        if not name.endswith(" RA"):
            name = name + " RA"

        if not name or name == "RA":
            flash("Team name cannot be empty.")
            return redirect(url_for(destination))

        if matches < 0:
            flash("Matches cannot be negative.")
            return redirect(url_for(destination))

        if fairplay_points < 0:
            flash("Fairplay points cannot be negative.")
            return redirect(url_for(destination))

        

        conn = get_db()

        team = conn.execute(
            """
            SELECT gender
            FROM teams
            WHERE id = ?
            """,
            (team_id,)
        ).fetchone()

        if team is None:
            conn.close()
            flash("Team not found.")
            return redirect(url_for(destination))

        if team["gender"] != gender:
            conn.close()
            flash("Invalid team update.")
            return redirect(url_for(destination))

        conn.execute(
            """
            UPDATE teams
SET
    name = ?,
    matches = ?,
    fairplay_points = ?,
    logo = ?
WHERE id = ?
            """,
            (
                (
    name,
    matches,
    fairplay_points,
    logo,
    team_id
)
            )
        )

        conn.commit()
        conn.close()

        flash("Team updated successfully.")

    except (TypeError, ValueError):
        flash("Please enter valid numbers.")

    return redirect(url_for(destination))


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# ============================================================
# START
# ============================================================

init_db()
if __name__ == "__main__":

    

    print("")
    print("==========================================")
    print("       IPL FAIRPLAY STANDINGS")
    print("==========================================")
    print("")
    print("Men's   : http://127.0.0.1:5000/mens")
    print("Women's : http://127.0.0.1:5000/womens")
    print("Admin   : http://127.0.0.1:5000/admin")
    print("")
    print("Admin username: admin")
    print("Admin password: admin123")
    print("")
    print("==========================================")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
