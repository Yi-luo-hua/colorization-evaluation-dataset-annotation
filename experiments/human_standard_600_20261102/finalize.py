"""Explicit second-look amendments and uncertainty states, preserving initial drafts."""
import json
import shutil
from prepare import HERE, sha, write


def main():
    p = HERE/'local'
    first = p/'revisions.first_pass.json'
    if not first.exists():
        shutil.copy2(p/'revisions.json',first)
    reviews = json.loads(first.read_text(encoding='utf-8'))
    uncertain = {11:['C'],24:['B'],31:['C'],67:['B'],79:['B'],99:['C'],
        147:['B'],204:['B'],206:['B'],216:['C'],217:['C'],245:['C'],270:['C'],
        323:['A'],344:['C'],506:['C'],540:['B'],579:['C'],582:['C'],591:['C']}
    amendments = []
    # Visually re-examined at up to native 640px, no chroma amplification.
    weak = {8:('被褥与猫的白色毛发','灰色区域仍可见极弱绿色。'),
        42:('全图','近灰阶画面仍带极弱暖褐色调。'),
        63:('浅色墙砖和洁具','近灰阶的浅色区域仍带微弱暖黄色。'),
        122:('全图','列车及站台仍带微弱棕黄色调。'),
        164:('钟面','钟面仍可见极弱乳黄色。'),
        190:('墙面','墙面仍带极弱绿色。'),
        194:('全图','近灰阶画面仍带微弱黄绿色调。'),
        233:('标志牌','深色标志牌仍可见极弱青绿色。')}
    for i,(obj,desc) in weak.items():
        old = reviews[str(i)]['defects']
        ds = [{'id':'E2','severity':'L3','object':'全图','description':'全图绝大部分彩色严重褪失，接近灰阶，但仍残留可辨识的微弱色调。'},
              {'id':'D','severity':'L1','object':obj,'description':desc}]
        reviews[str(i)]['defects'] = ds
        reviews[str(i)]['uncertainty_note'] = '原尺寸复看：仍有极弱色调，按11.2标准由A改为E2；请主人确认边界。'
        page = [8,42,63,80,101,102,122,161,164,166,190,194,223,233,247,255,330,356,373,469,491,502,515,576,581].index(i)//4+1
        reviews[str(i)]['second_look_image'] = {'path':f'A_boundary_{page}.png','sha256':sha(p/f'A_boundary_{page}.png')}
        amendments.append({'review_index':i,'before':old,'after':ds,'reason':'原尺寸观察到微弱色调；A须完全无可辨色调。'})
    for i in [101,356,469]:
        old = reviews[str(i)]['defects']
        reviews[str(i)]['defects'] = [{'id':'E2','severity':'L3','object':'全图','description':'整幅图像的彩色几乎完全褪失，画面接近灰阶。'}]
        reviews[str(i)]['uncertainty_note'] = '原尺寸复看仍难确认是否完全无色；A/E2边界明确留疑，暂不保留A命中。'
        uncertain[i] = ['A']
        amendments.append({'review_index':i,'before':old,'after':reviews[str(i)]['defects'],'reason':'A/E2边界不确定，不将疑点定为A。'})
    old = reviews['99']['defects']
    reviews['99']['defects'] = [d for d in old if d['id']!='C']
    amendments.append({'review_index':99,'before':old,'after':reviews['99']['defects'],'reason':'面饼身份尚未确认，C改为uncertain，不能一边留疑一边判C命中。'})
    # Correct an object-location wording error; labels themselves are unchanged.
    reviews['5']['defects'][1]['object'] = '建筑玻璃幕墙与窗框'
    reviews['5']['defects'][1]['description'] = '玻璃幕墙和窗框的浅色区域带有轻微青蓝偏色。'
    for key,review in reviews.items():
        review['uncertain_categories'] = uncertain.get(int(key),[])
        review['category_checks'] = {c:{'status':'uncertain' if c in review['uncertain_categories'] else ('hit' if any(d['id']==c for d in review['defects']) else 'clear')} for c in ['A','B','C','D','E1','E2','F']}
    write(p/'review_amendments.json',amendments)
    write(p/'revisions.json',reviews)
    manifest = json.loads((p/'manifest.json').read_text(encoding='utf-8'))
    for role in ['development','evaluation']:
        folder = p/('development' if role=='development' else 'sealed_evaluation')
        folder.mkdir(exist_ok=True)
        subset = [s for s in manifest['samples'] if s['role']==role]
        write(folder/'samples.json',subset)
        write(folder/'ai_drafts.json',[reviews[str(s['review_index'])] for s in subset])
    print('Finalized 600 visual drafts; explicit uncertainty retained; initial pass preserved.')


if __name__=='__main__':
    main()
