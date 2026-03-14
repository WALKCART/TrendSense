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
    clusters["date"] = pd.to_datetime(clusters["published"]).dt.date
    clusters.drop(columns=["published"], inplace=True)
    clusters["date"] = pd.to_datetime(clusters["date"])

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

def get_bursts(clusters, cluster_id, recent_days=2, baseline_days=7):
    """
    Compute burst score for a cluster based on recent article activity.

    burst_score = recent_rate / baseline_rate
    """
    if clusters.empty:
        return 0.0

    # ensure datetime
    clusters["published"] = pd.to_datetime(clusters["published"])

    # daily counts
    clusters["date"] = clusters["published"].dt.normalize()
    daily_counts = clusters.groupby("date").size().sort_index()

    if len(daily_counts) < 2:
        return 0.0

    last_date = daily_counts.index.max()

    recent_start = last_date - pd.Timedelta(days=recent_days - 1)
    baseline_start = last_date - pd.Timedelta(days=recent_days + baseline_days - 1)

    recent = daily_counts.loc[recent_start:last_date].sum()
    baseline = daily_counts.loc[baseline_start:recent_start - pd.Timedelta(days=1)].sum()

    recent_rate = recent / max(recent_days, 1)
    baseline_rate = baseline / max(baseline_days, 1)

    if baseline_rate == 0:
        return float(recent_rate)

    return float(recent_rate / baseline_rate)