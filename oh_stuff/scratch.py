def good_ar_bb(x0, x1, y0, y1, ar_t):

    dx = x1 - x0
    dy = y1 - y0

    x0_final = 0
    x1_final = 0
    y0_final = 0
    y1_final = 0

    ar_bb = dx/dy

    if ar_bb < ar_t:

        # too skinny

        y0_final = y0
        y1_final = y1

        dx_desired = dy * 3 / 4
        margin = round((dx_desired - dx) / 2)

        x0_final = x0 - margin
        x1_final = x1 + margin

    else:

        # too fat

        x0_final = x0
        x1_final = x1

        dy_desired = dx * 4 / 3
        margin = round((dy_desired - dy) / 2)

        y0_final = y0 - margin
        y1_final = y1 + margin

    return x0_final, x1_final, y0_final, y1_final