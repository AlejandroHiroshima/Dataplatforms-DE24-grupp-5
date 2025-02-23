import matplotlib as plt
def line_chart(x, y, **options):
    fig, ax = plt.subplots(1)

    ax.plot(x, y, linewidth=4)

    ax.set(**options)
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    plt.xticks(rotation=45)
    fig.tight_layout()
    return fig