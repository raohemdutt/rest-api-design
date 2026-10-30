"""Draws sequence-diagram.png, the UML sequence diagram for buying movie tickets online.

Run from this folder:  python3 make_diagram.py
Needs matplotlib. Every shape is placed by hand, so the diagram can be edited by
changing the text or the trip() calls at the bottom.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

W, H = 7.5, 8.7
CX, SX = 1.35, 6.15  # x position of the client and server lifelines
STEP = 1.12  # vertical space for one request/response round trip

fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")


def arrow(y, x0, x1, dashed=False):
    ax.add_patch(FancyArrowPatch(
        (x0, y), (x1, y), arrowstyle="->" if dashed else "-|>", mutation_scale=13,
        lw=1.3, color="black", ls="--" if dashed else "-", shrinkA=0, shrinkB=0))


def trip(y, n, title, req, resp):
    """One round trip: solid request arrow to the server, dashed response back."""
    ax.add_patch(Rectangle((CX - 0.07, y - 0.78), 0.14, 0.78, fc="white", ec="black", lw=1))
    ax.add_patch(Rectangle((SX - 0.07, y - 0.56), 0.14, 0.36, fc="white", ec="black", lw=1))
    arrow(y - 0.2, CX + 0.07, SX - 0.07)
    arrow(y - 0.56, SX - 0.07, CX + 0.07, dashed=True)
    mid = (CX + SX) / 2
    ax.text(mid, y - 0.05, f"{n}. {title}", ha="center", va="bottom", fontsize=9.5, fontweight="bold")
    ax.text(mid, y - 0.25, req, ha="center", va="top", fontsize=8.5, linespacing=1.25)
    ax.text(mid, y - 0.61, resp, ha="center", va="top", fontsize=8.5, linespacing=1.25)


def frame_top(y, kind, condition):
    """Top edge of an alt frame: operator tab plus the first guard condition."""
    ax.plot([0.25, W - 0.25], [y, y], color="#555", lw=1.1)
    ax.add_patch(Rectangle((0.25, y - 0.27), 0.55, 0.27, fc="#e8eef7", ec="#555", lw=1.1))
    ax.text(0.525, y - 0.135, kind, ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(CX + 0.25, y - 0.135, condition, ha="left", va="center", fontsize=8.5, style="italic")


top = H - 0.3
for x, label in ((CX, "Customer's Device\n(Client)"), (SX, "Movie Theater\nServer")):
    ax.add_patch(Rectangle((x - 0.8, top - 0.6), 1.6, 0.6, fc="#e8eef7", ec="black", lw=1.2))
    ax.text(x, top - 0.3, label, ha="center", va="center", fontsize=9.5, fontweight="bold")

ax.text((CX + SX) / 2, top - 0.3, "Every request carries the customer's\nauth token (Authorization header)",
        ha="center", va="center", fontsize=8, style="italic")

y = top - 0.9
trip(y, 1, "GET /showtimes  (find movie times)",
     "Request: movieId, date, zip code (or theaterId)",
     "Response: 200 OK, list of showtimes (showtimeId, time,\nauditorium, format, seats left)")
y -= STEP
trip(y, 2, "GET /showtimes/{showtimeId}/seats  (view seat map)",
     "Request: showtimeId, optional status filter",
     "Response: 200 OK, seats (seatId, row, number, type,\nstatus available/held/sold, price)")
y -= STEP
trip(y, 3, "POST /reservations  (select seats and hold them)",
     "Request: showtimeId, seatIds, customerEmail",
     "Response: 201 Created, reservationId, seatIds, total price,\nexpiresAt (10 minute hold). 409 if a seat was taken")
y -= STEP

# alt frame: the customer either pays (steps 4 and 5) or cancels (step 6)
frame_y0 = y + 0.12
frame_top(frame_y0, "alt", "[customer pays within the 10 minute hold]")
y = frame_y0 - 0.4
trip(y, 4, "POST /payments  (pay for the tickets)",
     "Request: reservationId, card token, billing zip code",
     "Response: 200 OK, paymentId, status (approved),\namount charged. 402 if the card is declined")
y -= STEP
trip(y, 5, "GET /reservations/{reservationId}/tickets  (get e-ticket)",
     "Request: reservationId",
     "Response: 200 OK, confirmationCode, QR code, movie,\nshowtime, auditorium, seats")
y -= STEP

divider = y + 0.14
ax.plot([0.25, W - 0.25], [divider, divider], color="#555", lw=1.1, ls=(0, (6, 3)))
ax.text(CX + 0.25, divider - 0.14, "[else customer cancels or changes their mind]",
        ha="left", va="center", fontsize=8.5, style="italic")
y = divider - 0.4
trip(y, 6, "DELETE /reservations/{reservationId}  (release the hold)",
     "Request: reservationId",
     "Response: 204 No Content (seats released).\n404 if unknown, 410 if the hold already expired")
frame_y1 = y - 1.0
ax.add_patch(Rectangle((0.25, frame_y1), W - 0.5, frame_y0 - frame_y1, fc="none", ec="#555", lw=1.1))

for x in (CX, SX):
    ax.plot([x, x], [top - 0.6, frame_y1 - 0.12], color="black", lw=1, ls=(0, (6, 4)), zorder=0)

out = Path(__file__).with_name("sequence-diagram.png")
fig.savefig(out, dpi=220)
print("wrote", out, "bottom margin", round(frame_y1, 2))
