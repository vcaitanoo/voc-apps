package pt.vcaitano.jarvis.voice

import android.content.Context
import org.json.JSONArray
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sin
import kotlin.math.sqrt

object VoicePrint {
    private const val PREFS="jarvis_voice";private const val KEY_CEPSTRUM="owner_mean_mfcc";private const val KEY_PITCH="owner_pitch_hz"
    const val SAMPLE_RATE=16_000;private const val FRAME_SIZE=400;private const val FRAME_HOP=160;private const val FFT_SIZE=512;private const val MEL_FILTERS=26;private const val NUM_COEFFS=13;private const val MIN_PCM_BYTES=11_520;private const val COS_PASS=0.86;private const val COS_STRICT=0.93;private const val PITCH_MIN_RATIO=0.55;private const val PITCH_MAX_RATIO=1.85
    fun isEnrolled(context:Context):Boolean=context.getSharedPreferences(PREFS,Context.MODE_PRIVATE).getString(KEY_CEPSTRUM,null)?.isNotBlank()==true
    fun clear(context:Context){context.getSharedPreferences(PREFS,Context.MODE_PRIVATE).edit().clear().apply()}
    fun enroll(context:Context,pcmLe16:ByteArray):Boolean{val features=extract(pcmLe16)?:return false;val(mean,pitch)=features;val array=JSONArray();mean.forEach{array.put(it)};context.getSharedPreferences(PREFS,Context.MODE_PRIVATE).edit().putString(KEY_CEPSTRUM,array.toString()).putString(KEY_PITCH,pitch.toString()).apply();return true}
    fun matches(context:Context,pcmLe16:ByteArray):Boolean{val prefs=context.getSharedPreferences(PREFS,Context.MODE_PRIVATE);val stored=prefs.getString(KEY_CEPSTRUM,null)?.takeIf{it.isNotBlank()}?:return true;val features=extract(pcmLe16)?:return true;val(mean,pitch)=features;val json=JSONArray(stored);val reference=DoubleArray(json.length()){json.optDouble(it)};if(reference.size!=mean.size)return true;var dot=0.0;var normRef=0.0;var normNew=0.0;for(i in reference.indices){dot+=reference[i]*mean[i];normRef+=reference[i]*reference[i];normNew+=mean[i]*mean[i]};val cosine=dot/(sqrt(normRef)*sqrt(normNew)+1e-9);if(cosine>=COS_STRICT)return true;val storedPitch=prefs.getString(KEY_PITCH,null)?.toDoubleOrNull()?:0.0;val ratio=if(storedPitch>1.0&&pitch>1.0)pitch/storedPitch else 1.0;return cosine>=COS_PASS&&ratio in PITCH_MIN_RATIO..PITCH_MAX_RATIO}
    private fun extract(pcmLe16:ByteArray):Pair<DoubleArray,Double>?{
        if(pcmLe16.size<MIN_PCM_BYTES)return null;val sampleCount=pcmLe16.size/2;val samples=ShortArray(sampleCount);for(i in 0 until sampleCount){val lo=pcmLe16[2*i].toInt() and 0xFF;val hi=pcmLe16[2*i+1].toInt();samples[i]=((hi shl 8) or lo).toShort()};val frameCount=if(sampleCount>=FRAME_SIZE)(sampleCount-FRAME_SIZE)/FRAME_HOP+1 else 0;if(frameCount<8)return null
        val window=DoubleArray(FRAME_SIZE){n->0.54-0.46*cos(2.0*PI*n/(FRAME_SIZE-1))};val filters=melFilterbank();val vectors=ArrayList<DoubleArray>(frameCount);val energies=DoubleArray(frameCount);val pitches=ArrayList<Double>(frameCount);val re=DoubleArray(FFT_SIZE);val im=DoubleArray(FFT_SIZE);val spectrum=DoubleArray(FFT_SIZE/2+1);val melEnergies=DoubleArray(MEL_FILTERS);val frame=DoubleArray(FRAME_SIZE);var index=0
        for(f in 0 until frameCount){var rmsSum=0.0;for(n in 0 until FRAME_SIZE){val s=samples[index+n].toDouble();rmsSum+=s*s;frame[n]=s*window[n]};energies[f]=sqrt(rmsSum/FRAME_SIZE);index+=FRAME_HOP;for(i in 0 until FRAME_SIZE){re[i]=frame[i];im[i]=0.0};for(i in FRAME_SIZE until FFT_SIZE){re[i]=0.0;im[i]=0.0};fft(re,im);for(k in spectrum.indices)spectrum[k]=re[k]*re[k]+im[k]*im[k];for(b in 0 until MEL_FILTERS){var acc=0.0;val filter=filters[b];for(k in spectrum.indices){val w=filter[k];if(w>0.0)acc+=w*spectrum[k]};melEnergies[b]=ln(maxOf(acc,1e-10))};val vector=DoubleArray(NUM_COEFFS);for(k in 1..NUM_COEFFS){var sum=0.0;for(n in 0 until MEL_FILTERS)sum+=melEnergies[n]*cos(PI*k*(n+0.5)/MEL_FILTERS);vector[k-1]=sum};vectors.add(vector);val pitch=framePitch(samples,index-FRAME_HOP);if(pitch>0.0)pitches.add(pitch)}
        val sorted=energies.clone();sorted.sort();val median=sorted[sorted.size/2];var kept=vectors.filterIndexed{i,_->energies[i]>median*0.55};if(kept.size<8){val order=vectors.indices.sortedByDescending{i->energies[i]};kept=order.take(maxOf(8,vectors.size/2)).map{vectors[it]}};val meanVector=DoubleArray(NUM_COEFFS);for(v in kept)for(i in 0 until NUM_COEFFS)meanVector[i]+=v[i]/kept.size;var norm=0.0;for(d in meanVector)norm+=d*d;norm=sqrt(norm)+1e-9;for(i in meanVector.indices)meanVector[i]/=norm;val pitchMedian=if(pitches.isEmpty())0.0 else{val p=pitches.toDoubleArray();p.sort();p[p.size/2]};return meanVector to pitchMedian
    }
    private fun framePitch(samples:ShortArray,offset:Int):Double{val minLag=50;val maxLag=270;var bestLag=-1;var bestCorr=0.0;var energySelf=0.0;for(n in 0 until FRAME_SIZE){val v=samples[offset+n].toDouble();energySelf+=v*v};if(energySelf<1e6)return 0.0;for(lag in minLag..maxLag){var corr=0.0;var energyLagged=0.0;for(n in 0 until FRAME_SIZE-lag){val a=samples[offset+n].toDouble();val b=samples[offset+n+lag].toDouble();corr+=a*b;energyLagged+=b*b};val normalized=corr/(sqrt(energySelf*energyLagged)+1e-9);if(normalized>bestCorr){bestCorr=normalized;bestLag=lag}};if(bestLag<=0||bestCorr<0.32)return 0.0;return SAMPLE_RATE/bestLag.toDouble()}
    private fun melFilterbank(): Array<DoubleArray> {
        fun hzToMel(hz: Double): Double = 2595.0 * ln(1.0 + hz / 700.0)
        fun melToHz(mel: Double): Double = 700.0 * (exp(mel / 2595.0) - 1.0)

        val nyquist = SAMPLE_RATE / 2.0
        val melMax = hzToMel(nyquist)
        val points = DoubleArray(MEL_FILTERS + 2) { b ->
            melToHz(melMax * b / (MEL_FILTERS + 1))
        }
        val bins = points.map { hz ->
            abs((FFT_SIZE + 1).toDouble() * hz / SAMPLE_RATE).toInt()
        }

        return Array(MEL_FILTERS) { b ->
            val filter = DoubleArray(FFT_SIZE / 2 + 1)
            val left = bins[b]
            val center = bins[b + 1]
            val right = bins[b + 2]
            for (k in left until center.coerceAtMost(filter.size)) {
                if (center > left) filter[k] = (k - left).toDouble() / (center - left)
            }
            for (k in center until right.coerceAtMost(filter.size)) {
                if (right > center) filter[k] = (right - k).toDouble() / (right - center)
            }
            filter
        }
    }
    private fun fft(re:DoubleArray,im:DoubleArray){val n=re.size;var j=0;for(i in 1 until n){var bit=n shr 1;while(j and bit!=0){j=j xor bit;bit=bit shr 1};j=j or bit;if(i<j){val t=re[i];re[i]=re[j];re[j]=t;val t2=im[i];im[i]=im[j];im[j]=t2}};var len=2;while(len<=n){val angle=-2.0*PI/len;val stepRe=cos(angle);val stepIm=sin(angle);var start=0;while(start<n){var curRe=1.0;var curIm=0.0;for(k in 0 until len/2){val aRe=re[start+k];val aIm=im[start+k];val bIndex=start+k+len/2;val bRe=re[bIndex]*curRe-im[bIndex]*curIm;val bIm=re[bIndex]*curIm+im[bIndex]*curRe;re[start+k]=aRe+bRe;im[start+k]=aIm+bIm;re[bIndex]=aRe-bRe;im[bIndex]=aIm-bIm;val nextRe=curRe*stepRe-curIm*stepIm;curIm=curRe*stepIm+curIm*stepRe;curRe=nextRe};start+=len};len=len shl 1}}
}
