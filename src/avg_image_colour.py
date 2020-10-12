
# adapted from:
# https://gist.github.com/olooney/1246268#file-average_image_color-py <3


def average(i):
    h = i.histogram()

    # split into red, green, blue
    r = h[0:256]
    g = h[256:256 * 2]
    b = h[256 * 2: 256 * 3]

    # perform the weighted average of each channel:
    # the *index* is the channel value, and the *value* is its weight
    return (
        sum(i * w for i, w in enumerate(r)) / sum(r),
        sum(i * w for i, w in enumerate(g)) / sum(g),
        sum(i * w for i, w in enumerate(b)) / sum(b)
    )
