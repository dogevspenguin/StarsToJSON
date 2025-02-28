import pandas as pd
import json
import argparse

def format_ra(ra_deg):
    hours_total = ra_deg
    hours = int(hours_total)
    remaining_minutes = (hours_total - hours) * 60
    minutes = int(remaining_minutes)
    seconds = (remaining_minutes - minutes) * 60
    return f"{hours:02d}H{minutes:02d}M{seconds:06.2f}S"

def format_dec(dec_deg):
    sign = '-' if dec_deg < 0 else '+'
    abs_deg = abs(dec_deg)
    degrees = int(abs_deg)
    remaining_deg = abs_deg - degrees
    arcminutes_total = remaining_deg * 60
    arcminutes = int(arcminutes_total)
    arcseconds = (arcminutes_total - arcminutes) * 60
    return f"{sign}{degrees:02d}D{arcminutes:02d}M{arcseconds:06.2f}S"

def get_star_name(row):
    if pd.notna(row['proper']):
        return row['proper']
    elif pd.notna(row['bf']):
        return row['bf']
    elif pd.notna(row['gl']):
        return row['gl']
    else:
        return f"HIP {row['hip']}"

def main(n, output_file):
    df = pd.read_csv("hygdata_v40.csv")

    df_filtered = df[(df['proper'] != 'Sol') & 
                     (~df['mag'].isna()) & 
                     (~df['dist'].isna())]

    df_sorted = df_filtered.sort_values('mag', ascending=True)
    top_n = df_sorted.head(n)

    stars_list = []
    for _, row in top_n.iterrows():
        name = get_star_name(row)
        ra = format_ra(row['ra'])
        dec = format_dec(row['dec'])
        spec = row['spect']
        appmag = round(row['mag'], 4)
        dist_ly = round(row['dist'] * 3.261563777167443, 2)
        stars_list.append({
            'NAME': name,
            'RA': ra,
            'DEC': dec,
            'APPMAG': appmag,
            'DIST': f"{dist_ly:.2f}LY",
            'SPEC': spec
        })

    with open(output_file, 'w') as f:
        json.dump(stars_list, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a JSON file of the brightest N stars.')
    parser.add_argument('-n', type=int, default=10, help='Number of brightest stars to include')
    parser.add_argument('-o', '--output', type=str, default='brightest_stars.json', help='Output JSON file name')
    args = parser.parse_args()

    main(args.n, args.output)