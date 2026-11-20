#define main candidate_cli_main
#include "fast_candidate.cpp"
#undef main

int reference(const vector<int>& s) {
    int n=(int)s.size(),ans=0;
    vector<int> d(n);
    for(int i=0,l=0,r=-1;i<n;++i){
        int k=i>r?1:min(d[l+r-i],r-i+1);
        while(i-k>=0&&i+k<n&&s[i-k]==s[i+k])++k;
        d[i]=k;ans=max(ans,2*k-1);
        if(i+k-1>r){l=i-k+1;r=i+k-1;}
    }
    fill(d.begin(),d.end(),0);
    for(int i=0,l=0,r=-1;i<n;++i){
        int k=i>r?0:min(d[l+r-i+1],r-i+1);
        while(i-k-1>=0&&i+k<n&&s[i-k-1]==s[i+k])++k;
        d[i]=k;ans=max(ans,2*k);
        if(i+k-1>r){l=i-k;r=i+k-1;}
    }
    return ans;
}
int slow(const vector<int>&s){int ans=0,n=(int)s.size();for(int l=0;l<n;++l)for(int r=l;r<n;++r){bool ok=true;for(int x=l,y=r;x<y;++x,--y)if(s[x]!=s[y]){ok=false;break;}if(ok)ans=max(ans,r-l+1);}return ans;}
long long checks=0,changes=0;
void verify(Engine&e,const vector<int>&s){
    if(e.materialize()!=s)throw runtime_error("piece contents mismatch");
    int a=e.query(),b=reference(s);
    if(a!=b)throw runtime_error("query mismatch: candidate="+to_string(a)+" reference="+to_string(b));
    if(s.size()<=12&&b!=slow(s))throw runtime_error("reference disagreement");
    if(e.stats.maxPieces>size_t(1+3*e.block))throw runtime_error("piece bound exceeded");
    ++checks;
}
int main(int argc,char**argv){
    unsigned long long seed=argc>1?stoull(argv[1]):9137;
    int trials=argc>2?stoi(argv[2]):200;
    mt19937_64 rng(seed);
    try{
        // Enumerate every binary initial string up to length 6 and every one-step operation.
        for(int n=1;n<=6;++n)for(int mask=0;mask<(1<<n);++mask){
            vector<int>s(n);for(int i=0;i<n;++i)s[i]=(mask>>i&1)?1000000000:0;
            Engine original(s,1);verify(original,s);
            for(int l=0;l<n;++l){
                for(int c:{0,1,1000000000}){Engine e(s,1);auto t=s;e.change(l,c);t[l]=c;verify(e,t);e.reverseRange(0,n);reverse(t.begin(),t.end());verify(e,t);changes+=2;}
                for(int r=l+1;r<=n;++r){
                    {Engine e(s,2);auto t=s;e.reverseRange(l,r);reverse(t.begin()+l,t.begin()+r);verify(e,t);++changes;}
                    for(long long k=0;k<=r-l+1;++k){Engine e(s,2);auto t=s;e.rotateRange(l,r,k);int shift=(int)(k%(r-l));rotate(t.begin()+l,t.begin()+r-shift,t.begin()+r);verify(e,t);++changes;}
                }
            }
        }
        cout<<"EXHAUSTIVE PASS seed="<<seed<<" checks="<<checks<<" updates="<<changes<<'\n';
        for(int trial=0;trial<trials;++trial){
            int n=1+rng()%700,mode=trial%5;
            vector<int>s(n);int a=rng()%1000000001,b=rng()%1000000001;
            vector<int>fib{a},prev{b};while((int)fib.size()<n){auto x=fib;x.insert(x.end(),prev.begin(),prev.end());prev.swap(fib);fib.swap(x);}
            for(int i=0;i<n;++i)s[i]=mode==0?a:mode==1?(i%2?a:b):mode==2?(int)(rng()%3):mode==3?(int)(rng()%1000000001):fib[i];
            int blockValues[]={1,2,7,31,128,1000};int B=blockValues[trial%6];
            Engine e(s,B);verify(e,s);
            for(int step=0;step<150;++step){
                int l=rng()%n,r=l+1+rng()%(n-l),op=rng()%3;
                if(step%17==0)l=0,r=n;
                if(op==0){int val=mode<2?(rng()%2?a:b):(int)(rng()%1000000001);if(step%19==0)val=1000000000;e.change(l,val);s[l]=val;}
                else if(op==1){e.reverseRange(l,r);reverse(s.begin()+l,s.begin()+r);}
                else{long long k=(long long)(rng()%1000000000000000001ULL);if(step%11==0)k=0;e.rotateRange(l,r,k);int shift=(int)(k%(r-l));rotate(s.begin()+l,s.begin()+r-shift,s.begin()+r);}
                ++changes;verify(e,s);
            }
        }
        cout<<"RANDOM PASS seed="<<seed<<" trials="<<trials<<" total_checks="<<checks<<" updates="<<changes<<'\n';
    }catch(const exception&e){cerr<<"FAIL seed="<<seed<<" checks="<<checks<<" "<<e.what()<<'\n';return 1;}
    return 0;
}
