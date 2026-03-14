import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
import numpy as np

# plot customization
plt.style.use('ggplot')
plt.rcParams['font.family'] = 'SF Mono'
plt.rcParams['font.size'] = 10
plt.figure(figsize=(40, 16))   # options: 'serif', 'sans-serif', 'monospace'
colors =[ "#1D2E50",'#334879','#8EB4E3','#D7E0F4']
colorsSorted = [ "#1D2E50",'#334879','#8EB4E3','#D7E0F4'][::-1]
sns.set_palette(colors)

def get_half_life(clusters, cluster_id, get_visualization=False):
    # getting the date
    clusters['date'] = clusters.published.apply(lambda x: x.split(' ')[0])
    clusters.drop(columns=['published'], inplace=True)
    clusters['date'] = pd.to_datetime(clusters['date'])

    # sorting by date 
    clusters = clusters.sort_values(
        by='date'
    )

    # choose cluster
    g = clusters[clusters['l1_cluster_id'] == cluster_id]

    # daily article counts
    daily_counts = g.groupby('date').size()

    # cumulative counts
    cum_counts = daily_counts.cumsum()

    # normalize to CDF
    cdf = cum_counts / cum_counts.max()

    # convert dates -> numeric time
    t = (cdf.index - cdf.index.min()).days.values
    y = cdf.values

    # exponential CDF model
    def exp_cdf(t, lam):
        return 1 - np.exp(-lam*t)

    # fit
    
    popt, _ = curve_fit(exp_cdf, t, y, p0=[0.1])
    lam = popt[0]
    half_life = np.log(2) / lam
    
    if get_visualization: 
        # smooth curve
        t_fit = np.linspace(0, t.max()*5, 200)
        y_fit = exp_cdf(t_fit, lam)

        # convert back to dates
        date_fit = cdf.index.min() + pd.to_timedelta(t_fit, unit='D')

        fig, ax = plt.subplots(figsize=(12,6))
        ax.scatter(cdf.index, y, label="Empirical CDF")
        ax.plot(date_fit, y_fit, linewidth=3, label="Exponential fit")

        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative article fraction")
        ax.set_title(f"Cluster {cluster_id} (half-life : {half_life:.2f} days)")
        ax.legend()

        fig.savefig('test.png', dpi=300)
    return half_life