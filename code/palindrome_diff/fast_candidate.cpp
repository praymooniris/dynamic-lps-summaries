#include <bits/stdc++.h>
using namespace std;

// Reference implementation: exact, deterministic; alphabet values are 0..1e9.
// Input: n q, n integers, then q operations (see README.md).
// Query: 4. Updates use 1-based closed intervals.
struct RMQ {
    vector<vector<int> > t;
    vector<int> lg;
    bool maximum = false;
    void build(const vector<int>& a, bool mx) {
        maximum = mx;
        int n = (int)a.size();
        lg.assign(n + 1, 0);
        for (int i = 2; i <= n; ++i) lg[i] = lg[i / 2] + 1;
        t.clear(); t.push_back(a);
        for (int k = 1; (1LL << k) <= n; ++k) {
            int m = n - (1 << k) + 1;
            t.push_back(vector<int>(m));
            for (int i = 0; i < m; ++i) {
                int x = t[k-1][i], y = t[k-1][i + (1 << (k-1))];
                t[k][i] = mx ? max(x,y) : min(x,y);
            }
        }
    }
    int get(int l, int r) const {
        if (l > r) return 0;
        int k = lg[r-l+1];
        int x = t[k][l], y = t[k][r-(1<<k)+1];
        return maximum ? max(x,y) : min(x,y);
    }
};
struct SuffixIndex {
    vector<int> text, rank;
    RMQ rmq;
    explicit SuffixIndex(const vector<int>& s): text(s) {
        int n = (int)s.size();
        vector<int> alphabet = s;
        sort(alphabet.begin(), alphabet.end());
        alphabet.erase(unique(alphabet.begin(), alphabet.end()), alphabet.end());
        rank.resize(n);
        vector<int> sa(n), tmp(n), buf(n), count(n+1);
        iota(sa.begin(), sa.end(), 0);
        for (int i=0;i<n;++i)
            rank[i] = (int)(lower_bound(alphabet.begin(),alphabet.end(),s[i])-alphabet.begin())+1;
        for (int k=1;;k*=2) {
            fill(count.begin(),count.end(),0);
            for (int a:sa) ++count[a+k<n ? rank[a+k] : 0];
            for (int i=1;i<=n;++i) count[i]+=count[i-1];
            for (int i=n-1;i>=0;--i) {
                int a=sa[i]; buf[--count[a+k<n ? rank[a+k] : 0]]=a;
            }
            fill(count.begin(),count.end(),0);
            for (int a:buf) ++count[rank[a]];
            for (int i=1;i<=n;++i) count[i]+=count[i-1];
            for (int i=n-1;i>=0;--i) { int a=buf[i]; sa[--count[rank[a]]]=a; }
            tmp[sa[0]]=1;
            for (int i=1;i<n;++i) {
                int a=sa[i-1],b=sa[i];
                tmp[b]=tmp[a]+(rank[a]!=rank[b] ||
                    (a+k<n ? rank[a+k]:0)!=(b+k<n ? rank[b+k]:0));
            }
            rank.swap(tmp);
            if (rank[sa.back()]==n) break;
        }
        for (int& x:rank) --x;
        vector<int> lcp(n);
        int h=0;
        for (int i=0;i<n;++i) {
            int z=rank[i];
            if (!z) { h=0; continue; }
            int j=sa[z-1];
            while (i+h<n && j+h<n && s[i+h]==s[j+h]) ++h;
            lcp[z]=h;
            if (h) --h;
        }
        rmq.build(lcp,false);
    }
    int lce(int a,int b) const {
        if (a==b) return (int)text.size()-a;
        int x=rank[a],y=rank[b];
        if (x>y) swap(x,y);
        return rmq.get(x+1,y);
    }
};
struct PalNode {
    int len,link=0,diff=0,series=0;
    map<int,int> next;
    explicit PalNode(int l=0):len(l) {}
};
struct Eertree {
    vector<PalNode> t;
    vector<int> last;
    vector<vector<int> > up;
    explicit Eertree(const vector<int>& s) {
        t.reserve(s.size()+2);
        t.emplace_back(-1); t.emplace_back(0);
        int cur=1;
        for (int i=0;i<(int)s.size();++i) {
            int x=cur,c=s[i];
            while (i-1-t[x].len<0 || s[i-1-t[x].len]!=c) x=t[x].link;
            auto it=t[x].next.find(c);
            if (it==t[x].next.end()) {
                int v=(int)t.size();
                t.emplace_back(t[x].len+2);
                t[x].next[c]=v;
                if (t[v].len==1) t[v].link=1;
                else {
                    int y=t[x].link;
                    while (i-1-t[y].len<0 || s[i-1-t[y].len]!=c) y=t[y].link;
                    t[v].link=t[y].next.at(c);
                }
                t[v].diff=t[v].len-t[t[v].link].len;
                t[v].series=(t[v].diff==t[t[v].link].diff) ? t[t[v].link].series : t[v].link;
                cur=v;
            } else cur=it->second;
            last.push_back(cur);
        }
        int levels=1;
        while ((1LL<<levels)<=(int)t.size()) ++levels;
        up.assign(levels,vector<int>(t.size()));
        for (int v=0;v<(int)t.size();++v) up[0][v]=t[v].link;
        for (int j=1;j<levels;++j)
            for (int v=0;v<(int)t.size();++v) up[j][v]=up[j-1][up[j-1][v]];
    }
    int start(int end,int cap) const {
        int v=last[end];
        if (t[v].len>cap) {
            for (int j=(int)up.size()-1;j>=0;--j)
                if (t[up[j][v]].len>cap) v=up[j][v];
            v=t[v].link;
        }
        return v;
    }
};
struct IntervalPal {
    RMQ odd,even;
    explicit IntervalPal(const vector<int>& s) {
        int n=(int)s.size(); vector<int> o(n),e(n);
        for (int i=0,l=0,r=-1;i<n;++i) {
            int k=i>r?1:min(o[l+r-i],r-i+1);
            while (i-k>=0 && i+k<n && s[i-k]==s[i+k]) ++k;
            o[i]=k--;
            if (i+k>r) {l=i-k;r=i+k;}
        }
        for (int i=0,l=0,r=-1;i<n;++i) {
            int k=i>r?0:min(e[l+r-i+1],r-i+1);
            while (i-k-1>=0 && i+k<n && s[i-k-1]==s[i+k]) ++k;
            e[i]=k--;
            if (i+k>r) {l=i-k-1;r=i+k;}
        }
        odd.build(o,true); even.build(e,true);
    }
    int query(int l,int r) const {
        int lo=1,hi=(r-l+2)/2,z=0;
        while (lo<=hi) {
            int m=(lo+hi)/2;
            if (odd.get(l+m-1,r-m+1)>=m) {z=m;lo=m+1;} else hi=m-1;
        }
        int ans=2*z-1;
        lo=1;hi=(r-l+1)/2;z=0;
        while (lo<=hi) {
            int m=(lo+hi)/2;
            if (even.get(l+m,r-m+1)>=m) {z=m;lo=m+1;} else hi=m-1;
        }
        return max(ans,2*z);
    }
};
struct Piece { int pos,len,value; }; // pos=-1 iff one literal symbol
using Pieces=vector<Piece>;
int total(const Pieces& v) { int n=0;for (auto p:v) n+=p.len;return n; }
Pieces cut(const Pieces& v,int off,int len) {
    Pieces out;
    if (len<=0) return out;
    for (auto p:v) {
        if (off>=p.len) {off-=p.len;continue;}
        int k=min(len,p.len-off);
        if (k) out.push_back({p.pos<0?-1:p.pos+off,k,p.value});
        len-=k;off=0;
        if (!len) break;
    }
    return out;
}
struct Stats {
    long long rebuilds=0,queries=0,series=0,indexLce=0,pieceSteps=0;
    size_t maxPieces=0;
};
struct Engine {
    int n,block,used=0;
    Pieces pieces;
    unique_ptr<SuffixIndex> sa;
    unique_ptr<Eertree> fw,bw;
    unique_ptr<IntervalPal> pal;
    Stats stats;
    Engine(const vector<int>& s,int b):n((int)s.size()),block(b) {rebuild(s);}
    void rebuild(const vector<int>& s) {
        // Release old indices before allocating new ones to limit peak memory.
        sa.reset();fw.reset();bw.reset();pal.reset();
        vector<int> rev=s;reverse(rev.begin(),rev.end());
        vector<int> all=s;all.push_back(-1);all.insert(all.end(),rev.begin(),rev.end());
        sa.reset(new SuffixIndex(all));
        fw.reset(new Eertree(s));bw.reset(new Eertree(rev));
        pal.reset(new IntervalPal(s));
        pieces={{0,n,0}};used=0;++stats.rebuilds;
        stats.maxPieces=max(stats.maxPieces,pieces.size());
    }
    vector<int> materialize() const {
        vector<int> a;a.reserve(n);
        for (auto p:pieces) {
            if (p.pos<0) a.push_back(p.value);
            else a.insert(a.end(),sa->text.begin()+p.pos,sa->text.begin()+p.pos+p.len);
        }
        return a;
    }
    Piece flip(Piece p) const {
        if (p.pos>=0) p.pos=2*n+1-p.pos-p.len;
        return p;
    }
    int split(int at) {
        int x=0;
        for (int i=0;i<(int)pieces.size();++i) {
            Piece p=pieces[i];
            if (x==at) return i;
            if (at<x+p.len) {
                int k=at-x;
                pieces[i].len=k;
                pieces.insert(pieces.begin()+i+1,{p.pos+k,p.len-k,p.value});
                return i+1;
            }
            x+=p.len;
        }
        return (int)pieces.size();
    }
    void prepare() {if (used==block) rebuild(materialize());}
    void finished() {++used;stats.maxPieces=max(stats.maxPieces,pieces.size());}
    void change(int i,int value) {
        prepare();int a=split(i),b=split(i+1);
        pieces.erase(pieces.begin()+a,pieces.begin()+b);
        pieces.insert(pieces.begin()+a,{-1,1,value});finished();
    }
    void reverseRange(int l,int r) {
        prepare();int a=split(l),b=split(r);
        reverse(pieces.begin()+a,pieces.begin()+b);
        for (int i=a;i<b;++i) pieces[i]=flip(pieces[i]);
        finished();
    }
    void rotateRange(int l,int r,long long k) {
        prepare();k%=r-l;
        if (k) {
            int a=split(l),b=split(r-(int)k),c=split(r);
            rotate(pieces.begin()+a,pieces.begin()+b,pieces.begin()+c);
        }
        finished();
    }
    int lce(const Pieces& a,const Pieces& b) {
        int i=0,j=0,x=0,y=0,ans=0;
        while (i<(int)a.size() && j<(int)b.size()) {
            ++stats.pieceSteps;
            Piece u=a[i],v=b[j];
            int cap=min(u.len-x,v.len-y),z;
            if (u.pos<0 || v.pos<0) {
                int c=u.pos<0?u.value:sa->text[u.pos+x];
                int d=v.pos<0?v.value:sa->text[v.pos+y];
                z=(c==d);
            } else {++stats.indexLce;z=min(cap,sa->lce(u.pos+x,v.pos+y));}
            ans+=z;if (z<cap) return ans;
            x+=z;y+=z;
            if (x==u.len) {++i;x=0;}
            if (y==v.len) {++j;y=0;}
        }
        return ans;
    }
    int periodic(const Pieces& v,Piece p) {
        int len=total(v),k=min(len,p.len);
        int a=lce(cut(v,0,k),Pieces{{p.pos,k,p.value}});
        if (a<k || len<=p.len) return a;
        return min(len,p.len+lce(v,cut(v,p.len,len-p.len)));
    }
    int boundary(const Pieces& r,const Pieces& y) {
        int len=total(r),ans=2*lce(r,y);
        Piece f=r[0];
        if (f.pos<0) return max(ans,1+2*lce(cut(r,1,len-1),y));
        bool reversed=f.pos>=n+1;
        int at=reversed?f.pos-(n+1):f.pos;
        const Eertree& t=reversed?*fw:*bw;
        int v=t.start(n-1-at,f.len);
        while (t.t[v].len>0) {
            ++stats.series;
            int D=t.t[v].len,p=t.t[v].diff,a=t.t[t.t[v].series].len+p;
            Pieces period=cut(r,D-p,p);
            if (period.size()!=1) throw runtime_error("period crosses first piece");
            int L=periodic(y,period[0]);
            int H=periodic(cut(r,D,len-D),period[0]);
            int K=(D-a)/p,q=(L-H)/p;
            int candidates[7]={0,K,q-2,q-1,q,q+1,q+2};
            for (int k:candidates) if (k>=0 && k<=K) {
                int d=D-k*p;
                ans=max(ans,d+2*lce(cut(r,d,len-d),y));
            }
            v=t.t[v].series;
        }
        return ans;
    }
    int query() {
        ++stats.queries;
        int ans=0,m=(int)pieces.size();
        for (int i=0;i<m;++i) {
            Piece p=pieces[i];
            if (p.pos<0) ans=max(ans,1);
            else {
                int at=p.pos<n?p.pos:2*n+1-p.pos-p.len;
                ans=max(ans,pal->query(at,at+p.len-1));
            }
            if (i+1<m) {
                Pieces r,y;
                for (int j=i;j>=0;--j) r.push_back(flip(pieces[j]));
                for (int j=i+1;j<m;++j) y.push_back(pieces[j]);
                ans=max(ans,boundary(r,y));
            }
            if (i>0) {
                Pieces r,y;
                for (int j=i;j<m;++j) r.push_back(pieces[j]);
                for (int j=i-1;j>=0;--j) y.push_back(flip(pieces[j]));
                ans=max(ans,boundary(r,y));
            }
        }
        return ans;
    }
};
int main(int argc,char**argv) {
    ios::sync_with_stdio(false);cin.tie(nullptr);
    int B=0;bool report=false;
    for (int i=1;i<argc;++i) {
        string a=argv[i];
        if (a=="--block" && i+1<argc) B=stoi(argv[++i]);
        else if (a=="--stats") report=true;
        else {cerr<<"Unknown argument: "<<a<<"\n";return 2;}
    }
    int n,q;if (!(cin>>n>>q)) return 2;
    if (n<1 || q<0) return 2;
    vector<int>s(n);for (int&x:s) {cin>>x;if(x<0||x>1000000000)return 2;}
    if (!B) B=max(1,(int)round(cbrt((double)n)));
    if (B<1) return 2;
    auto begin=chrono::steady_clock::now();
    Engine e(s,B);
    for (int i=0;i<q;++i) {
        int type;cin>>type;
        if (type==4) cout<<e.query()<<'\n';
        else if (type==1) {int p,c;cin>>p>>c;if(p<1||p>n||c<0||c>1000000000)return 2;e.change(p-1,c);}
        else if (type==2 || type==3) {
            int l,r;cin>>l>>r;if(l<1||l>r||r>n)return 2;
            if(type==2)e.reverseRange(l-1,r);
            else {long long k;cin>>k;if(k<0)return 2;e.rotateRange(l-1,r,k);}
        } else return 2;
        if (!cin) return 2;
    }
    if (report) {
        cerr<<"n="<<n<<" q="<<q<<" block="<<B
            <<" rebuilds="<<e.stats.rebuilds<<" max_pieces="<<e.stats.maxPieces
            <<" queries="<<e.stats.queries<<" series="<<e.stats.series
            <<" indexed_lce="<<e.stats.indexLce<<" piece_steps="<<e.stats.pieceSteps
            <<" seconds="<<chrono::duration<double>(chrono::steady_clock::now()-begin).count()<<'\n';
    }
    return 0;
}
