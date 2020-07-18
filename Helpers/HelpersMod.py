import bisect

class TTM:
    def __init__(self,t, M):
        x = (M - t)
        self.y =  x.days/365
        self.d = x.days


def lin_interp(x, df):
    a = list(df.columns)
    a.sort()
    df = df[a]
    index = bisect.bisect(df.columns, x)
    if index == 0 or index == len(df.columns):
        return df[df[index]]
    else:
        x1 = df.columns[index-1]
        x2 = df.columns[index]
        y1 = df[x1]
        y2 = df[x2]
        return (y2 -y1)/(x2 - x1)*(x-x1)+y1

def safe_get(row, col, message=None):
    try:
        a = row[col].iloc[0]
    except Exception:
        print(col, ' not found in ', row, ' Message: ', message)
        raise Exception
    return a

def cols_to_int(df):
    df1=df.copy()
    cols = list(df1)
    _num_cols = []
    for i in range(0,len(cols)):
        try:
            numb = int(cols[i])
            cols[i] = numb
            _num_cols.append(numb)
        except Exception:
            continue
    df1.columns = cols
    _num_cols.sort(reverse=True)
    all_cols = list(df1)
    for col in _num_cols:
        all_cols.insert(0, all_cols.pop(all_cols.index(col)))
    df1 = df1.ix[:, all_cols]
    df1.reset_index(drop=True,inplace=True)
    return df1


