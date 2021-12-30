import folium
from nltk.chunk import ne_chunk
from folium.plugins import MarkerCluster


def create_map():
    map = folium.Map(location=[50, 2], zoom_start=1.5)
    marker_cluster = MarkerCluster()
    map.add_child(marker_cluster)
    return map,marker_cluster


def add_Cluster_marker(marker_cluster,long,lat,content,score,user,date):
    #print(long,lat)
    if score>=0.05 :
        folium.Marker([float(long),float(lat)],popup= user + " a tweeté le " + date + ": \n" + content +"\n score : -"+str(score), icon=folium.Icon(color='green', icon='info-sign')).add_to(marker_cluster)
    elif score<=-0.05 :
        folium.Marker([float(long),float(lat)],popup= user + " a tweeté le " + date + ": \n" + content +"\n score : "+str(score), icon=folium.Icon(color='red')).add_to(marker_cluster)
    else :
        folium.Marker([float(long),float(lat)],popup= user + " a tweeté le " + date + ": \n" + content +"\n score : 0", icon=folium.Icon(color='blue')).add_to(marker_cluster)
    
    return marker_cluster

def save_map(map):
    map.save("static/map.html")
    
    #file = open("map.html",'a')
    #file.write("<script>setInterval(function(){window.open('file://C:/Users/gagni/OneDrive/Bureau/media_sociaux_5A/Twitter_Analyser_V3/index.html', '_self')}, 120000);</script>")
    
