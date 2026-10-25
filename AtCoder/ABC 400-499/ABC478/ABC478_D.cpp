#include <iostream>
#include <vector>

using namespace std;

vector<pair<int,int>> process(vector<pair<int,int>> &v) {
    vector<pair<int,int>> res;
    if (v.empty()) return res;
    sort(v.begin(), v.end());
    int l = v[0].first, r = v[0].second;
    for (int i = 1; i < v.size(); i++) {
        if (v[i].first <= r) {
            r = max(r, v[i].second);
        } else {
            res.push_back({l, r});
            l = v[i].first;
            r = v[i].second;
        }
    }
    res.push_back({l, r});
    return res;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, q; cin >> n >> q;
    vector<vector<pair<int,int>>> vals(q);
    for (int i = 0; i < q; i++) {
        int l, r, x; cin >> l >> r >> x;
        l--; r--; x--;
        vals[x].push_back({l, r});
    }

    vector<int> ans(n+1, 0);
    for (int i = 0; i < q; i++) {
        vector<pair<int,int>> v = process(vals[i]);
        for (auto &[l, r] : v) {
            ans[l]++;
            ans[r+1]--;
        }
    }
    for (int i = 1; i <= n; i++) {
        ans[i] += ans[i-1];
    }

    for (int i = 0; i < n; i++) {
        cout << ans[i] << " \n"[i == n-1];
    }
    return 0;
}